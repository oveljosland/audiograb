#!/usr/bin/env python3
#python -m src.main
import os
import time
import subprocess
#from .utils import getmnt
from google.cloud import storage

#CONFIG_FILE_NAME = 'config.json'




def upload_directory_to_bucket(upload_directory, bucket):
	uploaded = []
	for root, _, files in os.walk(upload_directory):
		for local_file in files:
			local_path = os.path.join(root, local_file)
			remote_path = local_path[len(upload_directory)+1:]
			blob = bucket.blob(remote_path)
			blob.upload_from_filename(local_path)
			uploaded.append(local_path)
	return uploaded


if __name__ == "__main__":
	start = time.strftime("%Y-%m-%d %H:%M:%S")

	"""
	mnt = getmnt()
	if mnt:
		print(f"mnt: {mnt}")
	else:
		# TODO: log: not mounted
		print("not mounted")
	"""

	test_dir = "src/test/upload"

	client = storage.Client.from_service_account_json("src/gcs_sa.json")
	bucket = client.bucket("audiograb-development")
	uploaded = upload_directory_to_bucket(test_dir, bucket)
	print(f"uploaded {len(uploaded)} files")

