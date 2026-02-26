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

	#upload_dir = create_upload_directory(config)
	#print(f"upload directory: {upload_dir}")

	"""
	temporary local
	"""
	upload_dir = 'upload'

	# offload files from storage device
	device.offload(mount_points, upload_dir)
	print(f"moved files from {mount_points} to {upload_dir}")

	transcode.transcode(upload_dir, config)

	exit(1)
	
	# unmount and power off device
	try:
		device.unmount_all_partitions(partitions)
		print("unmounted partitions")
		#device.power_off(device_path)
		#print("powered off device")

	except Exception as e:
		print(f"error while unmounting/powering off: {e}")

	
	#rtc.set_wakealarm_minutes(5)
	#rtc.disable()
	#rtc.print_kernel_info()


	# log: Battery voltage: bat.get_voltage()
	

	"""
	TODO:
	What are the rules for removing /tmp?
	- is it done on boot? if not: remove upload dir after upload
	"""

	





