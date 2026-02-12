#!/usr/bin/env python3
# python -m src.main

import os
import time
import json
import shutil
import uuid

import src.utils.device as device
import src.utils.conversion as conv


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


def upload_directory_to_bucket(upload_directory, bucket, config):
	uploaded = []
	for root, _, files in os.walk(upload_directory):
		for local_file in files:
			local_path = os.path.join(root, local_file)
			remote_path = local_path[len(upload_directory)+1:]
			blob = bucket.blob(remote_path)
			compressed = conv.compress_if_needed(local_path, config)
			blob.upload_from_filename(compressed)
			uploaded.append(local_path)
	return uploaded


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

	device_path = device.get_removable_devices()
	print(f"removable devices: {device_path}")

	if not device_path:
		exit(1)
	
	partitions = device.get_partitions(device_path)
	print(f"partitions: {partitions}")

	mount_points = device.mount_all_partitions(device_path)
	print(f"mount points: {mount_points}")

	upload_dir = create_upload_directory(config)
	print(f"upload directory: {upload_dir}")

	# offload files from storage device
	device.offload(mount_points, upload_dir)
	print(f"moved files from {mount_points} to {upload_dir}")

	# compress the upload directory
	cm = conv.compress_if_needed(upload_dir, config)
	print(f"compressed upload directory: {cm}")
	

	"""
	TODO:
	What are the rules for removing /tmp?
	- is it done on boot? if not: remove upload dir after upload
	"""


	# unmount and power off device
	try:
		
		device.unmount_all_partitions(partitions)
		print("unmounted partitions")

		"""
		device.power_off(device_path)
		print("powered off device")
		"""

	except Exception as e:
		print(f"error while unmounting/powering off: {e}")




