#!/usr/bin/env python3

# run from /src
# python -m audiograbd.main

import os
import time
import uuid
import subprocess
import logging

from audiograbd.utils.wakealarm import set_wakealarm, disable_wakealarm
from audiograbd.utils.device import offload
from audiograbd.utils.transcode import transcode
from audiograbd.utils.config import load_config
from audiograbd.utils.storage import GCSProvider
from audiograbd.models.speech import mute

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/tmp/audiograb.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)





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
	upload_dir = os.path.join(
		# if no project name is set, use audiograb as the name
		'/tmp', f"{config.get('project_name', 'audiograb')}-{timestamp}-{uid}"
	)
	os.makedirs(os.path.join(upload_dir, "data"), exist_ok=True)
	os.makedirs(os.path.join(upload_dir, "log", "telemetry"), exist_ok=True)
	return upload_dir





if __name__ == "__main__": 

	logger.info("Loading config...")

	try:
		config = load_config()
		logger.info("Config loaded")
	except RuntimeError as e:
		logger.error(f"Failed to load config: {e}")
		# when deployed
		#set_wakealarm(10)
		#halt()


	logger.info("Creating upload directory...")
	upload_directory = create_upload_directory(config)

	try:
		moved = offload_to(upload_directory)
	except RuntimeError as e:
		logger.error(f"failed to offload to {upload_directory}: {e}")
		"""
		TODO:
		
		What should be done if there are no devices connected?

		Suggestion:
			set_wakealarm(5)
			halt()
		"""
		


	

	logger.info("--- speech detection ---------------------")

	detect_speech = config.get("speech-detection", {})
	if detect_speech.get("enabled", False):
		logger.info("speech detection enabled")
		try:
			results = mute(upload_directory, debug=config.get("debug", False))
			for path, timestamps in results.items():
				logger.info(f"{path}: {len(timestamps)} speech segment(s)")
		except Exception as e:
			logger.error(f"speech detection failed: {e}")
	else:
		logger.info("speech detection disabled")
	
	logger.info("--- transcoding --------------------------")

	transcode(upload_directory, config)
	
	logger.info("--- uploading ----------------------------")

	exit(0)

	storage = config.get('storage', {})
	provider = storage.get('provider')
	if provider == "gcs":
		gcs_config = storage.get('gcs', {})
		bucket_name = gcs_config.get('bucket_name')
		if bucket_name is None:
			logger.error("bucket name missing from config")
		else:
			gcs = GCSProvider(bucket_name)
			gcs.upload(upload_directory)
	
	elif provider == "sigma2":
		# TODO: implement uploading to NIRD Sigma2
		pass
	else:
		logger.warning("no valid storage provider configured, skipping upload")


	logger.info("--- scheduling next alarm ----------------")
	# schedule the next wake alarm if the scheduler is enabled
	scheduler = config.get('scheduler', {})
	if scheduler.get('enabled'):
		interval = scheduler.get('interval_minutes')
		if interval is None or interval < 0:
			logger.warning(f"invalid wake interval ({interval})")
		else:
			logger.info(f"setting alarm to {interval} minutes")
			set_wakealarm(interval)

	
	# time to die
	halt()
	exit(0)


