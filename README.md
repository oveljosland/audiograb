# Audiograb
The Audiograb is an embedded wireless wildlife monitoring system, currently in development by students at NTNU for the Norwegian Institute of Nature Research ([NINA](https://www.nina.no/english/Home)). This repository contains the source code for the Audiograb system. The PCB design files are available [here](https://github.com/oveljosland/audiograb-pcb).

## Test Run
Clone the repo:
```
git clone https://github.com/oveljosland/audiograb
```
Navigate to the repo and source the virtual environment:
```
source venv/bin/activate
```
Install the packages:
```
pip install -r requirements.txt
```
Run the program as a module from the ``src/`` dir:
```
python -m audiograbd.main
```

## Repo info
The source code for `audiograbd` (the Audiograb Daemon) is in `src/audiograbd`, other source code is in `src/`.

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
