import gpiozero
import subprocess
from gpiozero import Device 
import gpiozero.pins.lgpio
from gpiozero.pins.lgpio import LGPIOFactory
import lgpio


class SD_interface:
	def __init__(self):
		factory = LGPIOFactory(chip=0)
		self.S_EN_SWITCH_pin = gpiozero.DigitalOutputDevice(pin=7, pin_factory=factory)
		self.R_EN_SWITCH_pin = gpiozero.DigitalOutputDevice(pin=12, pin_factory=factory)
		self.S_SWITCH_pin = gpiozero.DigitalOutputDevice(pin=8, pin_factory=factory) 
		self.R_SWITCH_pin = gpiozero.DigitalOutputDevice(pin=11, pin_factory=factory) 
		self.S_EN_VOUT_pin = gpiozero.DigitalOutputDevice(pin=17, pin_factory=factory) 
		self.R_EN_VOUT_pin = gpiozero.DigitalOutputDevice(pin=16, pin_factory=factory) 


def wait_for_quiet_SD_lines():
	"""
    Run c program to listen for activity on sd lines. 
    returns 1 if no activity, returns 0 if timeout is reached
 	"""
  
	timeout = subprocess.run(["sudo", "/home/jonas/folder/audiograb/src/pinctl/pinread"], capture_output=True)
 
	print("timeout:", timeout)

def init_sd_interface_pins():
	print("set pins \n")
	sd = SD_interface()
 
	sd.S_EN_SWITCH_pin.blink(on_time = 0.1, off_time = 0, n= 1, background = False)
	sd.S_SWITCH_pin.blink(on_time = 0.1, off_time = 0, n= 1, background = False)
	sd.S_EN_VOUT_pin.blink(on_time = 0.1, off_time = 0, n= 1, background = False)
	print("pins set")

def change_sd_host_to_ext():
	sd = SD_interface()
	sd.R_EN_SWITCH_pin.blink(on_time = 0.1,off_time = 1, n= 1, background = False) # off time is 1s to allow for sd card to shut down before switch
	sd.R_SWITCH_pin(on_time=0.1, off_time=0.1, n=1, background = False)
	sd.S_EN_SWITCH_pin(on_time=0.1,off_time=0, background=False)