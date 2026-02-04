import os
import json
import subprocess

MOUNTABLE_FILESYSTEMS = {"exfat", "vfat", "ext4", "ntfs"} # good enough

def get_block_devices_json():
	output = subprocess.run([
		"lsblk", "-J", "-b", # print size in bytes
		"-o", "NAME,TYPE,SIZE,RM,FSTYPE,MOUNTPOINTS" # only relevant fields
		],
		capture_output=True,
		text=True
	)
	return json.loads(output.stdout)


def has_mounted_partitions(device):
	return any(
		child.get("type") == "part" and
		child.get("mountpoints") for child in device.get("children", [])
	)


""" return list of all mountable partitions for a device """
def get_mountable_partitions(device):
	if has_mounted_partitions(device):
		return None

	partitions = []

	for partition in device.get("children", []):
		if partition.get("type") != "part":
			continue # skip non-partitions

		filesystem = partition.get("fstype")

		if filesystem not in MOUNTABLE_FILESYSTEMS:
			continue
		if partition.get("size", 0) < 16 << 20: # 16MB
			continue

		partitions.append(partition)

	return partitions if partitions else None
	

""" return list of removable devices with mountable partitions """
def get_removable_devices(return_largest=False):
	devices = get_block_devices_json()
	removable = []

	for device in devices['blockdevices']:
		if device.get('type') != 'disk':
			continue # skip non-disks
		if not device.get('rm'):
			continue # skip non-removable
		if not device.get('size', 0):
			continue # skip empty
		if device.get('mountpoints'):
			continue # skip already mounted
		if not device.get('children'):
			continue # skip if no partitions
		
		partitions = get_mountable_partitions(device)
		
		if not partitions:
				return None

		if return_largest:
			largest = max(partitions, key=lambda p: p["size"])
			return f"/dev/{largest['name']}"

		else:
			for partition in partitions:
				removable.append(f"/dev/{partition['name']}")

	return removable if removable else None