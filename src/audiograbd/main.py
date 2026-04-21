#!/usr/bin/env python3

# run from /src
# python -m audiograbd.main

import os
import time
import uuid
import subprocess
import logging

from audiograbd.utils.wakealarm import set_wakealarm, disable_wakealarm
from audiograbd.utils.device import offload
from audiograbd.utils.transcode import transcode
from audiograbd.utils.config import load_config
from audiograbd.utils.storage import GCSProvider
#from audiograbd.utils.model import speech_timestamps








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

	print("\n--- loading config file ------------------\n")

	try:
		config = load_config()
		print("config loaded")
	except RuntimeError as e:
		print(f"failed to load config: {e}")
		#set_wakealarm(10)
		#halt()

	#print(f"battery voltage: {get_battery_voltage()}V")
	#print(f"ntp synced     : {ntp_synced()}")

	print("\n--- finding removable devices ------------\n")

	upload_directory = create_upload_directory(config)

	try:
		moved = offload(upload_directory)
	except RuntimeError as e:
		print(f"failed to offload to {upload_directory}: {e}")
		"""
		TODO:
		
		What should be done if there are no devices connected?

		Suggestion:
			set_wakealarm(5)
			halt()
		"""
		


	

	print("\n--- speech detection ---------------------\n")
	
	"""
	TODO:
	"""
	#timestamps = speech_timestamps(upload_directory, config)
	#print("timestamps:")
	#print(timestamps)

	print("\n--- transcoding --------------------------\n")

	transcode(upload_directory, config)
	
	print("\n--- uploading ----------------------------\n")

	exit(0)

	storage = config.get('storage', {})
	provider = storage.get('provider')
	if provider == "gcs":
		gcs_config = storage.get('gcs', {})
		bucket_name = gcs_config.get('bucket_name')
		if bucket_name is None:
			print("bucket name missing from config")
		else:
			gcs = GCSProvider(bucket_name)
			gcs.upload(upload_directory)
	
	elif provider == "sigma2":
		# TODO: implement uploading to NIRD Sigma2
		pass
	else:
		print("no valid storage provider configured, skipping upload")


	print("\n--- scheduling next alarm ----------------\n")
	# schedule the next wakeup if the scheduler is enabled
	scheduler = config.get('scheduler', {})
	if scheduler.get('enabled'):
		interval = scheduler.get('interval_minutes')
		if interval is None or interval < 0:
			print(f"invalid wake interval ({interval})")
		else:
			print(f"setting alarm to {interval} minutes")
			set_wakealarm(interval)

	
	# time to die
	halt()

	"""
	NOTE: should never reach this point,
	but in the unlikely event it does we exit explicitly.	
	"""
	exit(0)


