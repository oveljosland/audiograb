# util

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