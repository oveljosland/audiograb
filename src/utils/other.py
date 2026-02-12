# util
import os
import json
import time
import socket
import subprocess

CONFIG_FILE_NAME = 'src/config/example.json'



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


