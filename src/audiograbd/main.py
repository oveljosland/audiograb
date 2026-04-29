#!/usr/bin/env python3

# run from /src
# python -m audiograbd.main

import os
import time
import uuid
import subprocess
import logging

from pathlib import Path

from audiograbd.utils.logger import configure_logging
from audiograbd.utils.wakealarm import set_wakealarm, disable_wakealarm
from audiograbd.utils.device import offload_to
from audiograbd.utils.transcode import transcode
from audiograbd.utils.config import load_config
from audiograbd.utils.storage import GCSProvider
from audiograbd.models.speech import mute


logger = logging.getLogger(__name__)


"""
TODO:

What should be done if there are no devices connected?

Suggestion:
	set_wakealarm(5)
	halt()
"""


def halt():
	"""Tell the OS to halt the system.
	The `POWER_OFF_ON_HALT` EEPROM flag must be set to `1`.
	"""
	try:
		subprocess.run(["systemctl", "halt"], check=True)
	except Exception as e:
		logger.error(f"failed to halt: {e}")



def create_upload_directory(config):
	"""Create upload directory in `/tmp` with a timestamp and UUID.
	On Raspberry Pi OS, `/tmp` is a `tmpfs`, which means it will be erased when shutting down.
	"""
	timestamp = time.strftime(config.get('date_time_format', "%Y%m%d-%H%M%S"))
	uid = str(uuid.uuid4())[:8]

	project_name = config.get('project_name', 'audiograb')

	base = Path("/tmp") / f"{project_name}-{timestamp}-{uid}"

	# create subdirectories
	(base / "data").mkdir(parents=True, exist_ok=True)
	(base / "log" ).mkdir(parents=True, exist_ok=True)

	return base





if __name__ == "__main__": 

	logger.info("Loading config...")

	try:
		config = load_config(force_backup=True)
		configure_logging(config)
		logger.info("Config loaded")
	except RuntimeError as e:
		logger.error(f"Failed to load any config file: {e}")
		if config.get('scheduler', {}).get('enabled', False):
			logger.info(f"Waking up in 10 minutes to try again...")
		set_wakealarm(10)
		halt()


	
	upload_directory = create_upload_directory(config)
	logger.info(f"Create upload directory at {upload_directory}...")

	try:
		logger.info(f"Offloading data from all removable devices...")
		moved = offload_to(upload_directory)
	except RuntimeError as e:
		logger.error(f"Failed to offload to {upload_directory}: {e}")



	detect_speech = config.get("speech-detection", {})
	if detect_speech.get("enabled", False):
		logger.info("Speech detection enabled")
		try:
			results = mute(upload_directory, debug=config.get("debug", False))
			for path, timestamps in results.items():
				logger.info(f"{path}: {len(timestamps)} speech segment(s)")
		except Exception as e:
			logger.error(f"Speech detection failed: {e}")
	else:
		logger.info("Speech detection disabled")
	
	logger.info("Transcoding files...")
	transcode(upload_directory, config)
	
	exit(0)
	storage = config.get('storage', {})
	provider = storage.get('provider')
	if provider == "gcs":
		gcs_config = storage.get('gcs', {})
		bucket_name = gcs_config.get('bucket_name')
		if bucket_name is None:
			logger.error("GCS bucket name missing from config")
		else:
			gcs = GCSProvider(bucket_name)
			gcs.upload(upload_directory)
	
	elif provider == "sigma2":
		username = storage.get('sigma2', {}).get('username')
		port = storage.get('sigma2', {}).get('port')
		sigma2 = Sigma2Provider()
		sigma2.upload("/home/jonas/folder/test_file.txt", str(username), port) #TODO: Need a testfile path
	else:
		logger.warning("No valid storage provider configured, skipping upload")


	logger.info("Scheduling next alarm...")
	scheduler = config.get('scheduler', {})
	if scheduler.get('enabled'):
		interval = scheduler.get('interval_minutes')
		if interval is None or interval < 0:
			logger.warning(f"Invalid wake interval ({interval})")
		else:
			logger.info(f"Next wake alarm scheduled in {interval} minutes")
			set_wakealarm(interval)

	
	# time to die
	logger.info("Halting...")
	halt()
	exit(0)


