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


def mount(device):
	return subprocess.run([
		"udisksctl", "mount", "-b", device
	],
	capture_output=True,
	text=True
	)

def unmount(device):
	return subprocess.run([
		"udisksctl", "unmount", "-b", device
	],
	capture_output=True,
	text=True
	)

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