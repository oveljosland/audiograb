#!/usr/bin/env python3
#python -m src.main

import time
import subprocess
from .utils import getmnt

def sysconfig(sd_mount_directory, sd_card):
	working_directory_name = 'monitoring-tmp'
	upload_directory_name = 'audio'
	working_directory = os.path.join('/tmp', working_directory_name)
	local_upload_directory = upload_directory_name

	if sd_card:
		upload_directory = os.path.join(sd_mount_directory, upload_directory_name)
		
		if os.path.exists(local_upload_directory) and os.path.isdir(local_upload_directory):
			# TODO: merge dirs
	else:
		upload_directory = local_upload_directory

	project_id = 'NA'
	config_id = 'NA'
	cpu_serial = get_cpu_serial()

if __name__ == "__main__":
	start = time.strftime("%Y-%m-%d %H:%M:%S")
	mnt = getmnt()
	if mnt:
		print(f"mnt: {mnt}")
	else:
		# TODO: log: not mounted
		print("not mounted")