# Audiograb
The Audiograb is an embedded wireless wildlife monitoring system, currently in development by students at NTNU for the Norwegian Institute of Nature Research ([NINA](https://www.nina.no/english/Home)). This repository contains the source code for the Audiograb system. The PCB design files are available [here](https://github.com/oveljosland/audiograb-pcb).

## Quick Start
Install packages:
```
sudo apt install git ffmpeg pkexec -y
```
Clone the repo:
```
git clone https://github.com/oveljosland/audiograb
```
Create a virtual environment:
```
python -m venv venv
```
Source it:
```
source venv/bin/activate
```
Install modules:
```
pip install -r requirements.txt
```
Run the program:
```
python -m audiograbd.main
```

## Before field deployment
Edit bootloader configuration to enable the system to wake at configurable intervals:
```
sudo -E rpi-eeprom-config --edit
```

Add the following lines:
```
POWER_OFF_ON_HALT=1
WAKE_ON_GPIO=0
```
