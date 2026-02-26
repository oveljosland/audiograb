#!/usr/bin/env python3
# python -m src.main

import os
import time
import json
import shutil
import uuid
import subprocess

import src.utils.rtc as rtc
import src.utils.bat as bat
import src.utils.device as device
import src.utils.transcode as transcode


"""
TODO:
What are the rules for removing /tmp?
- is it done on boot? if not: remove upload dir after upload
"""



def halt():
	"""
	Ask the OS to halt the system.
	The `POWER_OFF_ON_HALT' EEPROM flag must be set to `1'.
	"""
	try:
		subprocess.run(["shutdown", "-h", "now"], check=True)
	except Exception as e:
		print(f"failed to halt: {e}")

def sysctlhalt():
	"""
	Ask the OS to halt the system.
	The `POWER_OFF_ON_HALT' EEPROM flag must be set to `1'.
	"""
	try:
		subprocess.run(["systemctl", "halt"], check=True)
	except Exception as e:
		print(f"failed to halt: {e}")


def ntp_synced():
	output = subprocess.run(
		["timedatectl", "show", "-p", "NTPSynchronized", "--value"],
		capture_output=True,
		text=True
	)
	return output.stdout.strip() == "yes"


def load_config(path):
	with open(path, "r") as f:
		return json.load(f)


def create_upload_directory(config):
	timestamp = time.strftime(config.get('date_time_format', "%Y%m%d-%H%M%S"))
	uid = str(uuid.uuid4())[:8] # unique id
	upload_dir = os.path.join(
		'/tmp', f"{config.get('project_name', 'audiograb')}-{timestamp}-{uid}"
	)
	os.makedirs(os.path.join(upload_dir, "data"), exist_ok=True)
	os.makedirs(os.path.join(upload_dir, "log", "telemetry"), exist_ok=True)
	return upload_dir


def copy_testmedia(mount_point):
    for i in os.listdir("testmedia"):
        src = os.path.join("testmedia", i)
        dst = os.path.join(mount_point, i)
        if os.path.isdir(src):
            shutil.copytree(src, dst, dirs_exist_ok=True)
        else:
            shutil.copy2(src, dst)


if __name__ == "__main__": 

	"""
	TODO:
	- check if new config available from server
	"""
	config = load_config('src/config/example.json')

	start_time = time.strftime(config.get('date_time_format', "%Y%m%d-%H%M%S"))

	print(f"battery voltage: {bat.get_voltage()}V")
	print(f"ntp synced: {ntp_synced()}")

	device_path = device.get_removable_devices()
	print(f"removable devices: {device_path}")

	if not device_path:
		exit(1)
	
	partitions = device.get_partitions(device_path)
	print(f"partitions: {partitions}")

	mount_points = device.mount_all_partitions(device_path)
	print(f"mount points: {mount_points}")

	copy_testmedia(mount_points[0])

	#upload_dir = create_upload_directory(config)
	#print(f"upload directory: {upload_dir}")

	# temporary local dir for testing
	upload_dir = 'upload'

	# device.offload returns the list of files that were moved,
	# might useful for telemetry in the future
	moved = device.offload(mount_points, upload_dir)
	print(f"moved {len(moved)} files from {mount_points} to {upload_dir}")

	transcode.transcode(upload_dir, config)

	"""
	stop before cleanup
	"""
	#exit(0)

	# prepare for shutdown
	device.cleanup(device_path, partitions)

	# schedule the next wakeup if the scheduler is enabled
	scheduler = config.get('scheduler', {})
	if scheduler.get('enabled'):
		interval = scheduler.get('interval_minutes')
		if interval is None or interval < 0:
			print(f"invalid wake interval ({interval})")
		else:
			print(f"setting alarm to {interval} minutes")
			rtc.set_wakealarm_minutes(interval)

	# time to die
	sysctlhalt()

	"""
	NOTE: should never reach this point,
	but in the unlikely event it does we exit explicitly.	
	"""
	exit(0)


# org.freedesktop.login1.halt