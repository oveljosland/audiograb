import os
import re
import json
import shutil
import subprocess



def get_block_devices_json():
	output = subprocess.run([
		"lsblk", "-J", "-b", # print size in bytes
		"-o", "NAME,TYPE,SIZE,RM,FSTYPE,MOUNTPOINTS" # only relevant fields
		],
		capture_output=True,
		text=True
	)
	return json.loads(output.stdout)



def get_removable_devices():
	devices = get_block_devices_json()
	removable = []

	for device in devices['blockdevices']:
		if device.get('type') != 'disk':
			continue # skip non-disks
		if not device.get('rm'):
			continue # skip non-removable
		if not device.get('size', 0):
			continue # skip empty

		if not device.get('children'):
			continue # skip if no partitions

		# return device path
		return f"/dev/{device['name']}"



def get_partitions(device_path, return_largest=False):
	devices = get_block_devices_json()
	for device in devices['blockdevices']:
		if f"/dev/{device['name']}" == device_path:
			partitions = device.get("children", [])
			if return_largest and partitions:
				largest = max(partitions, key=lambda p: p["size"])
				return [f"/dev/{largest['name']}"]
			return [f"/dev/{p['name']}" for p in partitions]
	return []



def mount(device_path):
	output = subprocess.run([
		"udisksctl", "mount", "-b", device_path
	],
	capture_output=True,
	text=True
	)
	if "already mounted" in output.stderr or output.returncode != 0:
		# find mount point
		devices = get_block_devices_json()
		for device in devices['blockdevices']:
			for child in device.get('children', []):
				if f"/dev/{child['name']}" == device_path:
					mounts = child.get('mountpoints', [])
					if mounts and mounts[0]:
						return mounts[0]
		# failed to find mount point
		raise RuntimeError(f"failed to mount {device_path}: {output.stderr}")
	
	return output.stdout.split()[-1] # return mountpoint from stdout



def unmount(device_path):
	return subprocess.run([
		"udisksctl", "unmount", "-b", device_path
	],
	capture_output=True,
	text=True
	).stderr # return error



def mount_all_partitions(device_path):
	partitions = get_partitions(device_path)
	mount_points = []
	for partition in partitions:
		mount_point = mount(partition)
		mount_points.append(mount_point)
	return mount_points



def unmount_all_partitions(device_paths):
	for device_path in device_paths:
		unmount(device_path)



def power_off(device_path):
	# normalise, /dev/sda2 -> /dev/sda
	device_path = re.sub(r"\d+$", "", device_path)

	return subprocess.run([
		"udisksctl", "power-off", "-b", device_path
	],
	capture_output=True,
	text=True,
	check=True,
	).stdout


# offload files from mount points to dest, categorising dirs
def offload(mount_points, dest):
	"""
	TODO:
	- return list of moved files
	"""
	def categorise_path(path):
		path = path.lower()
		if 'log' in path or 'telemetry' in path:
			return os.path.join('log', 'telemetry')
		return 'data'
	moved = []
	for mnt in mount_points:
		for root, _, files in os.walk(mnt):
			for file in files:
				src = os.path.join(root, file)
				print(f"src: {src}")
				rel = os.path.relpath(src, mnt)
				print(f"rel: {rel}")
				cat = categorise_path(rel)
				print(f"cat: {cat}")
				dst = os.path.join(dest, cat, rel)
				print(f"dst: {dst}")
				os.makedirs(os.path.dirname(dst), exist_ok=True)
				shutil.move(src, dst)


"""
def power_off_device(device):

Arranges for the drive to be safely removed and powered off.
On the OS side this includes ensuring that no process is using the drive, then
requesting that in-flight buffers and caches are committed to stable storage.
The exact steps for powering off the drive depends on the drive itself and the interconnect used.
For drives connected through USB, the effect is that the USB device will be deconfigured followed by
disabling the upstream hub port it is connected to.

Note that as some physical devices contain multiple drives (for example 4-in-1 flash card reader USB devices) powering off one drive may affect other drives.
As such there are not a lot of guarantees associated with performing this action.
Usually the effect is that the drive disappears as if it was unplugged.

	output = subprocess.run([
		"udisksctl", "power-off", device
	],
	capture_output=True,
	text=True
	)
"""