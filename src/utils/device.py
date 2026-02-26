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



def offload(mount_points, dest):
	"""
	Move every file found under ``mount_points'' into the local
	``dest'' directory.

	The files are categorised by their path such that telemetry/logs end up in
	``dest/log/telemetry'' and everything else in ``dest/data''.  A list of the
	absolute destination paths is returned.

	The implementation is intentionally simple; it does not attempt to preserve
	timestamps or handle name conflicts.  Those behaviours can be added if the
	requirements ever demand them.
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
				moved.append(dst)
	return moved

	