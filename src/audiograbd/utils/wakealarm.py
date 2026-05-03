import subprocess
import logging

logger = logging.getLogger(__name__)


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



def print_kernel_info() -> None:
	"""Print RTC kernel info."""
	output = subprocess.run([
		"cat", KERNEL_INFO_RTC
		],
		capture_output=True,
		text=True
	)
	logger.debug(f"RTC kernel info: {output.stdout}")



def set_wakealarm(minutes: int) -> None:
	"""Set next wake alarm in minutes."""
	if minutes < 0 or minutes is None:
		logger.warning(f"Invalid wake interval ({minutes}), skipping wake alarm")
		return
	output = subprocess.run(
		["pkexec", "usr/local/bin/wakealarm", str(minutes*60)],
		capture_output=True,
		text=True
	)
	if output.returncode != 0 or not alarm_irq_enabled():
		raise RuntimeError(f"Failed to set wake alarm: {output.stderr}")



def disable_wakealarm() -> None:
	"""Disable the wake alarm."""
	set_wakealarm(0)