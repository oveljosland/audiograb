# modem driver

INET_RETRIES = 15

def check_internet_connectivity(timeout=3):
	try:
		socket.setdefaulttimeout(timeout)
		socket.create_connection(("1.1.1.1", 53))
		return True
	except OSError:
		return False

def wait_for_internet_connection(tries, timeout=2):
	connected = False
	for t in range(tries):
		connected = check_internet_connectivity(timeout)
	
		if connected:
			break
	
		else:
			# should maybe log some of this
			time.sleep(1)
	
	if connected:
		print("connected to the internet")
		# light up some LEDs
	else:
		print(f"no connection after {t+1}/{tries}")

	return connected