# util
import os
import json
import time
import socket
import subprocess

CONFIG_FILE_NAME = 'src/config/example.json'


def setup_directories(sd_mount_directory, sd_card):
	working_directory_name = 'monitoring-tmp'
	upload_directory_name = 'audio'
	working_directory = os.path.join('/tmp', working_directory_name)
	local_upload_directory = upload_directory_name

	if sd_card:
		upload_directory = os.path.join(sd_mount_directory, upload_directory_name)
		
		if os.path.exists(local_upload_directory) and os.path.isdir(local_upload_directory):
			# TODO: merge dirs (Why)
			pass
	else:
		upload_directory = local_upload_directory

	project_id = 'NA'
	config_id = 'NA'
	cpu_serial = read_cpu_serial()

	if os.path.exists(CONFIG_FILE_NAME):
		with open(CONFIG_FILE_NAME) as f:
			device_config = json.load(f)['device']
			project_id = device_config['project_id']
			config_id = device_config['config_id']

	project_directory = os.path.join(upload_directory, 'project_{}'.format(project_id))
	device_directory = os.path.join(project_directory, 'device_{}'.format(cpu_serial))
	data_directory = os.path.join(device_directory, 'config_{}'.format(config_id))

	return working_directory, upload_directory, data_directory


def read_cpu_serial():
	error = "NO_CPU_SERIAL"
	try:
		with open('/proc/cpuinfo', 'r') as f:
			for line in f:
				if line.startswith('Serial'):
					return line.split(":", 1)[1].strip()
	except OSError:
		pass
	return error


def ntp_synced():
	output = subprocess.run(
		["timedatectl", "show", "-p", "NTPSynchronized", "--value"],
		capture_output=True,
		text=True
	)
	return output.stdout.strip() == "yes"


