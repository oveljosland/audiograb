#!/usr/bin/env python3

# run from /src
# python -m audiograbd.main

import os
import time
import uuid
import subprocess
import logging
import argparse
import threading

from pathlib import Path

from audiograbd.utils.logger import configure_logging
from audiograbd.utils.wakealarm import set_wakealarm, disable_wakealarm
from audiograbd.utils.device import offload_to, copy_testmedia_to_removable_devices
from audiograbd.utils.transcode import transcode
from audiograbd.utils.config import load_config, load_backup
from audiograbd.utils.storage import GCSProvider, Sigma2Provider
from audiograbd.models.silero import detect_and_mute
from audiograbd.utils.server import serve


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





def create_upload_dir(config):
	"""Create upload dir in `/tmp` with a project name,
	timestamp and UUID. The upload dir is not peristent."""
	name = config.get('project_name', 'audiograb')
	date = time.strftime(config.get('date_time_format', "%Y%m%d-%H%M%S"))
	base = Path("/tmp") / f"{name}-{date}-{str(uuid.uuid4())[:8]}"
	(base / "data").mkdir(parents=True, exist_ok=True)
	(base / "logs").mkdir(parents=True, exist_ok=True)
	logger.info(f"Created upload directory at {base}")
	return base





if __name__ == "__main__":

	start_time = time.time()

	parser = argparse.ArgumentParser(description="audiograbd - extract, process, and upload audio from embedded wildlife recorders")
	parser.add_argument('--serve-port', type=int, default=None, 
		help="Start a web server to browse processed files")
	args = parser.parse_args()

	
	logger.info("Loading config...")

	try:
		#config = load_config()
		config = load_backup()
		
	except RuntimeError as e:
		logger.error(f"Failed to load config: {e}")
		if config.get('scheduler', {}).get('enabled', False):
			logger.info(f"Waking up in 10 minutes to try again...")
		set_wakealarm(10)
		halt()

	upload_dir = create_upload_dir(config)
	data_dir = upload_dir / "data"
	logs_dir = upload_dir / "logs"

	project_name = config.get('project_name', 'audiograb')
	configure_logging(config, file=logs_dir / f"{project_name}.log")
	
	
	

	# put test media on all connected removable devices
	copy_testmedia_to_removable_devices()

	try:
		logger.info(f"Offloading data from all removable devices...")
		offload_start = time.time()
		moved = offload_to(data_dir)
		logger.info(f"Offloaded {len(moved)} files in {time.time() - offload_start:.2f} seconds")
	except RuntimeError as e:
		logger.error(f"Failed to offload to {upload_dir}: {e}")


	birdnet = config.get("birdnet-prediction", {})
	if birdnet.get("enabled", False):
		logger.info("BirdNET prediction enabled")
		try:
			pass
			"""
			TODO: implement BirdNET prediction.
			"""
		except Exception as e:
			logger.error(f"BirdNET prediction failed: {e}")
	else:
		logger.info("BirdNET prediction disabled")
	

	silero = config.get("speech-removal", {})
	if silero.get("enabled", False):
		logger.info("Speech removal enabled")
		silero_start = time.time()
		try:
			results = detect_and_mute(data_dir)
			logger.info(f"Speech removal completed in {time.time() - silero_start:.2f} seconds")
			for path, timestamps in results.items():
				logger.info(f"{path}: {len(timestamps)} speech segment(s)")
		except Exception as e:
			logger.error(f"Speech detection failed: {e}")
	else:
		logger.info("Speech detection disabled")
	
	
	logger.info("Transcoding files...")
	transcode_start = time.time()
	transcode(data_dir, config)
	logger.info(f"Transcoding completed in {time.time() - transcode_start:.2f} seconds")
	

	# start web server if audiograbd was run with --serve-port <port> 
	if args.serve_port:
		logger.info(f"Starting web server on port {args.serve_port}...")
		server_thread = threading.Thread(
			target=serve, args=(upload_dir, args.serve_port),
			daemon=True
		)
		server_thread.start()
		try:
			while True:
				time.sleep(1)
		except KeyboardInterrupt:
			logger.info("Stopping web server...")



	logger.info("Uploading files...")
	storage = config.get('storage', {})
	provider = storage.get('provider')

	upload_start = time.time()
	
	if provider == "gcs":
		gcs_config = storage.get('gcs', {})
		bucket_name = gcs_config.get('bucket_name')
		if bucket_name is None:
			logger.error("GCS bucket name missing from config")
		else:
			gcs = GCSProvider(bucket_name)
			gcs.upload(upload_dir)
	
	elif provider == "sigma2":
		username = storage.get('sigma2', {}).get('username')
		port = storage.get('sigma2', {}).get('port')
		sigma2 = Sigma2Provider()
	else:
		logger.warning("No valid storage provider configured, skipping upload")

	logger.info(f"Upload completed in {time.time() - upload_start:.2f} seconds")
	
	scheduler = config.get('scheduler', {})
	if scheduler.get('enabled'):
		interval = scheduler.get('interval_minutes')
		if interval is None or interval < 0:
			logger.warning(f"Invalid wake interval ({interval})")
		else:
			logger.info(f"Total running time: {time.time() - start_time:.2f} seconds")
			logger.info(f"Next wake alarm scheduled in {interval} minute(s)")
			set_wakealarm(interval)

			# time to die
			logger.info("Halting...")
			halt()
			exit(0)

	
	logger.info(f"Total running time: {time.time() - start_time:.2f} seconds")
	exit(0)


