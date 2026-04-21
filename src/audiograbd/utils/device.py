import os
import re
import json
import shutil
import subprocess



def get_block_devices_json():
	""" Returns a list of block devices as JSON. """
	output = subprocess.run([
		"lsblk", "-J", "-b", # print size in bytes
		"-o", "NAME,TYPE,SIZE,RM,FSTYPE,MOUNTPOINTS" # only relevant fields
		],
		capture_output=True,
		text=True
	)
	return json.loads(output.stdout)



def get_removable_devices():
	""" Returns the path of all removable block devices. """
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
	"""
	Returns the partitions of the device.
	Optionally return the largest partition.
	"""
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
	""" Mount the device, and return its mountpoint. """
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
	
	return output.stdout.split()[-1]



def unmount(device_path):
	""" Unmount the device. """
	return subprocess.run([
		"udisksctl", "unmount", "-b", device_path
	],
	capture_output=True,
	text=True
	).stderr # return error



def mount_all_partitions(device_path):
	""" Mount all the partitions of the device, return their mountpoints. """
	partitions = get_partitions(device_path)
	mount_points = []
	for partition in partitions:
		mount_point = mount(partition)
		mount_points.append(mount_point)
	return mount_points



def unmount_all_partitions(device_paths):
	""" Unmount all partitions of the device. """
	for device_path in device_paths:
		unmount(device_path)



def power_off(device_path):
	""" Power off the device. """
	# normalise, /dev/sda2 -> /dev/sda
	device_path = re.sub(r"\d+$", "", device_path)

	return subprocess.run([
		"udisksctl", "power-off", "-b", device_path
	],
	capture_output=True,
	text=True,
	check=True,
	).stdout



def move(mnt, dst):
	"""
	Move all files from `mnt` to `dst`.

	The files are categorised by their path such that telemetry and logs end up in
	`dst/log/telemetry` and everything else in `dst/data`.
	
	Returns a list of the absolute destination paths.
	"""

	def categorise_path(path):
		path = path.lower()
		if 'log' in path or 'telemetry' in path:
			return os.path.join('log', 'telemetry')
		return 'data'

	moved = []
	for m in mnt:
		for root, _, files in os.walk(m):
			for file in files:
				src = os.path.join(root, file)
				print(f"src: {src}")
				rel = os.path.relpath(src, m)
				print(f"rel: {rel}")
				cat = categorise_path(rel)
				print(f"cat: {cat}")
				dst = os.path.join(dst, cat, rel)
				print(f"dst: {dst}")
				os.makedirs(os.path.dirname(dst), exist_ok=True)
				shutil.move(src, dst)
				moved.append(dst)
	return moved


def copy_testmedia(mount_point):
	""" Copy media to mount point for testing. """
	for i in os.listdir("testmedia"):
		src = os.path.join("testmedia", i)
		dst = os.path.join(mount_point, i)
		if os.path.isdir(src):
			shutil.copytree(src, dst, dirs_exist_ok=True)
		else:
			shutil.copy2(src, dst)



def offload(dst):
	""" Offload all files to `dst`. """
	device_path = get_removable_devices()
	print(f"removable devices: {device_path}")

	if not device_path:
		raise RuntimeError("no removable devices found")

	partitions = get_partitions(device_path)
	print(f"partitions: {partitions}")

	mount_points = mount_all_partitions(device_path)
	print(f"mount points: {mount_points}")

	#copy_testmedia(mount_points[0]) #- testing

	moved = move(mount_points, dst)
	return moved
