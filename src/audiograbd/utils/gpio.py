import gpiozero
import subprocess


class SD_interface:
	def __init__(self):
		#factory = LGPIOFactory(chip=0)
		self.S_EN_SWITCH_pin = gpiozero.DigitalOutputDevice(pin=7)
		self.R_EN_SWITCH_pin = gpiozero.DigitalOutputDevice(pin=12)
		self.S_SWITCH_pin = gpiozero.DigitalOutputDevice(pin=8) 
		self.R_SWITCH_pin = gpiozero.DigitalOutputDevice(pin=11) 
		self.S_EN_VOUT_pin = gpiozero.DigitalOutputDevice(pin=17) 
		self.R_EN_VOUT_pin = gpiozero.DigitalOutputDevice(pin=16) 


def wait_for_quiet_SD_lines():
	"""
    Run c program to listen for activity on sd lines. 
    returns 1 if no activity, returns 0 if timeout is reached
 	"""
  
	timeout = subprocess.run(["/home/jonas/folder/audiograb/src/pinctl/pinread"], capture_output=True)
 
	#print("timeout:", timeout)

def init_sd_interface_pins():
	"""
	Initialises pins and set goes through rutine of setting sd card host
	"""
	
	sd = SD_interface()
 
	sd.S_EN_SWITCH_pin.blink(on_time = 0.1, off_time = 0, n= 1, background = False) #turn on swich
	sd.S_SWITCH_pin.blink(on_time = 0.1, off_time = 0, n= 1, background = False) #set switch to connect to external device
	sd.S_EN_VOUT_pin.blink(on_time = 0.1, off_time = 0, n= 1, background = False) #enable output voltage
	

def change_sd_host_to_cm():
	"""
	Goes through routine off changing the switch position to 
	connect sd card to compute module
	"""
	sd = SD_interface()
	sd.R_EN_SWITCH_pin.blink(on_time = 0.1,off_time = 1, n= 1, background = False) # off time is 1 s to allow for sd card to shut down before switch
	sd.R_SWITCH_pin(on_time=0.1, off_time=0.1, n=1, background = False) #set switch to connect to cm
	sd.S_EN_SWITCH_pin(on_time=0.1,off_time=0, background=False) # turn on switch outputs


def change_sd_host_to_ext():
	"""
	Goes through routine off changing the switch position to 
	connect sd card to compute module
	"""
	sd = SD_interface()
	sd.R_EN_SWITCH_pin.blink(on_time = 0.1,off_time = 1, n= 1, background = False) # off time is 1 s to allow for sd card to shut down before switch
	sd.S_SWITCH_pin(on_time=0.1, off_time=0.1, n=1, background = False) #set switch to connect to cm
	sd.S_EN_SWITCH_pin(on_time=0.1,off_time=0, background=False) # turn on switch outputs

