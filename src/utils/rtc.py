import subprocess
import json

SYSFS_WAKEALARM = '/sys/class/rtc/rtc0/wakealarm'
KERNEL_INFO_RTC = '/proc/driver/rtc'


def alarm_irq_enabled():
	output = subprocess.run([
		"grep", "alarm_IRQ", KERNEL_INFO_RTC
		],
		capture_output=True,
		text=True
	)
	output = output.stdout.split(":")[1].strip()
	return True if output == "yes" else False


def set_wakealarm_minutes(minutes, path=SYSFS_WAKEALARM):
	if minutes < 0 or minutes is None:
		"""
		TODO: log something like "interval value error"
		"""
		return
	
	output = subprocess.run([
		"wakectl", "-w", str(minutes*60), path
		],
		capture_output=True,
		check=True,
		text=True
	)

	if not alarm_irq_enabled():
		"""
		TODO: log failed to set wakealarm
		"""
		print(output.stdout)
		print(output.stderr)

def disable(path=SYSFS_WAKEALARM):
	output = subprocess.run([
		"wakectl", "-w", str(0), path
		],
		capture_output=True,
		check=True,
		text=True
	)
	
	if alarm_irq_enabled():
		"""
		TODO: log failed to disable wakealarm
		"""
		print(output.stdout)



def print_kernel_info(path=KERNEL_INFO_RTC):
	output = subprocess.run([
		"cat", path
		],
		capture_output=True,
		text=True
	)
	print(output.stdout)




