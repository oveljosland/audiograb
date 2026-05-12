import socket
import time
import logging

logger = logging.getLogger(__name__)

def check_internet_connectivity(timeout=3):
	"""Check internet connectivity."""
	try:
		socket.setdefaulttimeout(timeout)
		socket.create_connection(("1.1.1.1", 53))
		return True
	except OSError:
		return False

def wait_for_internet_connection(tries, timeout=2):
	"""Wait for internet connection."""
	connected = False
	for t in range(tries):
		connected = check_internet_connectivity(timeout)
	
		if connected:
			break
	
		else:
			# should maybe log some of this
			time.sleep(1)
	
	if connected:
		logger.info("Connected to the internet")
		# light up some LEDs
	else:
		logger.warning(f"No connection after {t+1}/{tries}")

	return connected