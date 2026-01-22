#!/usr/bin/env python3

import time
import subprocess

def getmnt():
	try:
		output = subprocess.run(
			["lsblk", "-o", "NAME,RM,MOUNTPOINT", "-nr"],
			capture_output=True,
			text=True,
			check=True
		)
		for l in output.stdout.splitlines():
			name, rm, mnt = line.split(maxsplit=2)
			if rm == "1" and mnt != "":
				return mnt
	except Exception:
		pass
	return None

if __name__ == "__main__":
	start = time.strftime("%Y-%m-%d %H:%M:%S")
	mnt = getmnt()
	if mnt:
		print(f"mnt: {mnt}")
	else:
		# log: not mounted?
		print("not mounted")