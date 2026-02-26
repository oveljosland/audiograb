#!/usr/bin/env python3
# python -m src.main

import os
import time
import json
import shutil
import uuid
import subprocess
import logging

import src.utils.rtc as rtc
from src.utils.bat import get_battery_voltage
from src.utils.device import offload
from src.utils.transcode import transcode
from src.utils.config import load_config








def halt():
	"""
	Ask the OS to halt the system.
	The `POWER_OFF_ON_HALT` EEPROM flag must be set to `1`.
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





def create_upload_directory(config):
	"""
	Create upload dir in `/tmp` with timestamp and uuid.
	On Raspberry Pi OS, `/tmp` is a `tmpfs`, which means
	it is stored in memory and will be erased on reboot.
	"""
	timestamp = time.strftime(config.get('date_time_format', "%Y%m%d-%H%M%S"))
	uid = str(uuid.uuid4())[:8] # unique id
	upload_dir = os.path.join(
		'/tmp', f"{config.get('project_name', 'audiograb')}-{timestamp}-{uid}"
	)
	os.makedirs(os.path.join(upload_dir, "data"), exist_ok=True)
	os.makedirs(os.path.join(upload_dir, "log", "telemetry"), exist_ok=True)
	return upload_dir





if __name__ == "__main__": 


	try:
		config = load_config()
		print("config loaded")
	except RuntimeError as e:
		print(f"failed to load config: {e}")
		exit(1)

	print(f"battery voltage: {get_battery_voltage()}V")
	print(f"ntp synced     : {ntp_synced()}")

	#upload_directory = create_upload_directory(config)
	upload_directory = 'upload'

	offload(upload_directory)
	transcode(upload_directory, config)

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
	halt()

	"""
	NOTE: should never reach this point,
	but in the unlikely event it does we exit explicitly.	
	"""
	exit(0)


