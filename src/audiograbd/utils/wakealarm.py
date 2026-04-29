import subprocess
import logging

logger = logging.getLogger(__name__)



SYSFS_WAKEALARM = '/sys/class/rtc/rtc0/wakealarm'
KERNEL_INFO_RTC = '/proc/driver/rtc'



def alarm_irq_enabled() -> bool:
	"""Returns True if the RTC IRQ alarm is set."""
	output = subprocess.run([
		"grep", "alarm_IRQ", KERNEL_INFO_RTC
		],
		capture_output=True,
		text=True
	)
	output = output.stdout.split(":")[1].strip()
	return True if output == "yes" else False



def set_wakealarm(minutes: int, path=SYSFS_WAKEALARM) -> None:
	"""Sets the wake alarm in minutes."""
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

	# check if the alarm has been set
	if not alarm_irq_enabled():
		"""
		TODO: log failed to set wakealarm
		"""
		logger.debug(f"wakectl stdout: {output.stdout}")
		logger.debug(f"wakectl stderr: {output.stderr}")



def disable_wakealarm(path=SYSFS_WAKEALARM):
	"""Disable the wake alarm."""
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
		logger.debug(f"wakectl stdout: {output.stdout}")



def print_kernel_info(path=KERNEL_INFO_RTC):
	"""Print RTC kernel info."""
	output = subprocess.run([
		"cat", path
		],
		capture_output=True,
		text=True
	)
	logger.debug(f"RTC kernel info: {output.stdout}")


