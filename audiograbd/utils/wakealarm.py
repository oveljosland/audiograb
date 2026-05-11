import os
import subprocess
import logging

logger = logging.getLogger(__name__)


KERNEL_INFO_RTC = '/proc/driver/rtc'


def alarm_irq_enabled() -> bool:
	"""Returns True if the RTC IRQ alarm is set."""
	output = subprocess.run(
		["grep", "alarm_IRQ", KERNEL_INFO_RTC],
		capture_output=True,
		text=True
	)
	if output.returncode != 0:
		return False
	parts = output.stdout.split(":", 1)
	if len(parts) != 2:
		return False
	return parts[1].strip() == "yes"



def set_wakealarm(minutes: int) -> None:
	"""Set next wake alarm in minutes."""
	if minutes is None or minutes < 0:
		logger.warning(f"Invalid interval ({minutes}), skipping alarm...")
		return
	interval = "0" if minutes == 0 else f"+{minutes * 60}"
	cmd = ["/usr/local/bin/wakealarm.sh", interval]
	if os.geteuid() != 0:
		cmd.insert(0, "pkexec")
	logger.debug(f"Setting alarm with: {cmd}")
	output = subprocess.run(
		cmd,
		capture_output=True,
		text=True
	)
	if output.returncode != 0 or not alarm_irq_enabled():
		raise RuntimeError(
			f"Failed to set alarm, returned {output.returncode})"
		)



def disable_wakealarm() -> None:
	"""Disable the wake alarm."""
	set_wakealarm(0)



# only used for debugging
def print_kernel_info() -> None:
	"""Print RTC kernel info."""
	output = subprocess.run([
		"cat", KERNEL_INFO_RTC
		],
		capture_output=True,
		text=True
	)
	logger.debug(f"RTC kernel info: {output.stdout}")