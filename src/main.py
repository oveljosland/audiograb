#!/usr/bin/env python3
# python -m src.main

import os
import time
import json

import src.utils.device as device
import src.utils.conversion as conv


from google.cloud import storage


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
			compressed = compress_if_needed(local_path, config)
			blob.upload_from_filename(compressed)
			uploaded.append(local_path)
	return uploaded


if __name__ == "__main__":
	start_time = time.strftime("%Y-%m-%d %H:%M:%S")
	config = load_config('src/config/example.json')

	device_path = device.get_removable_devices(return_largest=True)
	print(device_path)

	mount_point = device.mount(device_path)
	print(mount_point)

	unmount_error = device.unmount(device_path)
	if unmount_error:
		print(f"error unmounting: {device_path}")

	#print(device.power_off(device_path))



	#client = storage.Client.from_service_account_json("src/gcs_sa.json")
	#bucket = client.bucket("audiograb-development")
	#uploaded = upload_directory_to_bucket(test_dir, bucket, config)
	#print(f"uploaded {len(uploaded)} files")
	#print(time_synced())
