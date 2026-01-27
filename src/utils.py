# util
import socket
import subprocess

INET_RETRIES = 15



def sysconfig(sd_mount_directory, sd_card):
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
	cpu_serial = get_cpu_serial()

	if os.path.exists(CONFIG_FILE_NAME):
		device_config = json.load(open(CONFIG_FILE_NAME))['device']
		project_id = device_config['project_id']
		config_id = device_config['config_id']

	project_directory = os.path.join(upload_directory, 'project_{}'.format(project_id))
	device_directory = os.path.join(project_directory, 'device_{}'.format(cpu_serial))
	data_directory = os.path.join(device_directory, 'config_{}'.format(config_id))

	return working_directory, upload_directory, data_directory


# get mount point of removable disk
def getmnt():
	try:
		output = subprocess.run(
			["lsblk", "-o", "NAME,RM,MOUNTPOINT", "-nr"],
			capture_output=True,
			text=True,
			check=True
		)
		for line in output.stdout.splitlines():
			name, rm, mnt = line.split(maxsplit=2)
			if rm == "1" and mnt != "":
				return mnt
	except Exception:
		pass
	return None

def get_cpu_serial():
	error = "NO_CPU_SERIAL_ID"
	try:
		with open('/proc/cpuinfo', 'r') as f:
			for line in f:
				if line.startswith('Serial'):
					return line.split(":", 1)[1].strip()
	except OSError:
		pass
	return error


def has_internet_access(timeout=3):
	try:
		socket.setdefaulttimeout(timeout)
		socket.create_connection(("1.1.1.1", 53))
		return True
	except OSError:
		return False

def wait_for_internet(tries, timeout=2):
	connected = False
	for t in range(tries):
		connected = has_internet_access(timeout)
	
		if connected:
			break
	
		else:
			# should maybe log some of thisv
			time.sleep(1)
	
	if connected:
		print("connected to the internet")
		# light up some LEDs
	else:
		print(f"no connection after {t}/{tries}")

	return connected


	
def time_synced():
	output = subprocess.run(
		["timedatectl", "show", "-p", "NTPSynchronized", "--value"],
		capture_output=True,
		text=True
	)
	return output.stdout.strip() == "yes"