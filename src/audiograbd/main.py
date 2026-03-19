#!/usr/bin/env python3

# run from /src
# python -m audiograbd.main

import os
import time
import json
import shutil
import uuid
import subprocess
import logging


from audiograbd.utils.wakealarm import print_kernel_info
from audiograbd.utils.wakealarm import set_wakealarm, disable_wakealarm
from audiograbd.utils.bat import get_battery_voltage
from audiograbd.utils.device import offload
from audiograbd.utils.transcode import transcode
from audiograbd.utils.config import load_config
from audiograbd.utils.storage import GCSProvider
from audiograbd.utils.gpio import SD_interface, wait_for_quiet_SD_lines, init_sd_interface_pins, change_sd_host_to_cm, change_sd_host_to_ext
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

	#Jonas:
	#In python set swicth in correct position, enable switch, turn on external power
	#wait for quiet sd bus or timeout from c prog.
 
	print("\n--- Ensure gpio lines are set correct ------------\n")
	
	try:
		init_sd_interface_pins()
	except:
		print("Bad pin Factory")


	print("\n--- listening to sd lines and change sd host\n")
 
	try:
		wait_for_quiet_SD_lines()
	except:
		print("likely bad pinmanufacture")



	print("\n--- finding removable devices ------------\n")

	upload_directory = create_upload_directory(config)

	try:
		offload(upload_directory)
	except:
		print("no upload directory found")
	

	print("\n--- Unmount in system and change sd host")

	
	#do unmount of sd card	
	try:
		change_sd_host_to_cm()
	except:
		print("Likely bad pin factory ")


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
			sigma2 = sigma2Provider()
			sigma2.upload(upload_directory)
			print("simga2")
	else:
		print("no valid storage provider configured, skipping upload")


	exit(0)
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


