#!/usr/bin/env python3

import time
#import usb.core


# TODO: call 'lsusb' get mount location
#mntloc = pass

class CardReader:
	vendor = ''
	product = ''

reader = CardReader()

reader.vendor = 'banana'
reader.product = 'sd'

print(reader.vendor)
print(reader.product)


start_time = time.strftime("%Y-%m-%d %H:%M:%S")
print(start_time)

#dev = usb.core.find()
