#!/usr/bin/env python3

# run from /src
# python -m audiograbd.main

import os
import time
import uuid
import subprocess
import logging
import argparse
import http.server
import socketserver
import threading

from pathlib import Path

from audiograbd.utils.logger import configure_logging
from audiograbd.utils.wakealarm import set_wakealarm, disable_wakealarm
from audiograbd.utils.device import offload_to, copy_testmedia_to_removable_devices
from audiograbd.utils.transcode import transcode
from audiograbd.utils.config import load_config, load_backup
from audiograbd.utils.storage import GCSProvider, Sigma2Provider
from audiograbd.models.speech import mute
from audiograbd.utils.gpio import change_sd_host_to_cm, change_sd_host_to_ext, init_sd_interface_pins
from audiograbd.models.silero import mute


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


def serve_directory(directory, port):
	"""Start a simple HTTP server for the given directory.
	Runs in a background thread.
	"""
	directory = Path(directory)
	if not directory.exists():
		logger.warning(f"Directory does not exist: {directory}")
		return

	os.chdir(directory)
	handler = http.server.SimpleHTTPRequestHandler
	
	try:
		with socketserver.TCPServer(("", port), handler) as httpd:
			logger.info(f"Web server running on http://localhost:{port}")
			logger.info(f"Serving files from: {directory}")
			httpd.serve_forever()
	except Exception as e:
		logger.error(f"Failed to start web server: {e}")


def create_upload_directory(config, project_name):
	"""Create upload directory in `/tmp` with a timestamp and UUID.
	On Raspberry Pi OS, `/tmp` is a `tmpfs`, which means it will be erased when shutting down.
	"""
	timestamp = time.strftime(config.get('date_time_format', "%Y%m%d-%H%M%S"))
	uid = str(uuid.uuid4())[:8]

	base = Path("/tmp") / f"{project_name}-{timestamp}-{uid}"

	# create subdirectories
	(base / "data").mkdir(parents=True, exist_ok=True)
	(base / "logs" ).mkdir(parents=True, exist_ok=True)

	logger.info(f"Created upload directory at {base}")
	return base





if __name__ == "__main__": 
	parser = argparse.ArgumentParser(description="audiograbd - extract, process, and upload audio from embedded wildlife recorders")
	parser.add_argument('--serve-port', type=int, default=None, 
		help="Start a web server on this port to browse processed files")
	args = parser.parse_args()

	start_time = time.time()
	logger.info("Loading config...")

	try:
		
		#config = load_config()
		config = load_backup()

		# set project name, e.g. place of deployment
		project_name = config.get('project_name', 'audiograb')

		upload_dir = create_upload_directory(config, project_name)
		data_dir = upload_dir / "data"
		logs_dir = upload_dir / "logs"

		log_file = logs_dir / f"{project_name}.log"
		configure_logging(config, log_file=log_file)
	except RuntimeError as e:
		logger.error(f"Failed to load any config file: {e}")
		if config.get('scheduler', {}).get('enabled', False):
			logger.info(f"Waking up in 10 minutes to try again...")
		set_wakealarm(10)
		halt()


	#initialise gpio

	try:
		logger.info(f"initialising pins ")
		init_sd_interface_pins()
	except:
		logger.error(f"pins not initialized, possibly bad pin factory")

	#wait for quiet sd lines
	try:
		logger.info(f"waiting for quiet sd lines")

		if(wait_for_quiet_SD_lines()):
			change_sd_host_to_cm()
			logger.info(f"changes sd mux to CM")
		else:
			logger.info(f"timeout reached for waiting for quiet sd lines")
	except:
		logger.error(f"waiting for quiet sd lines failed")


	
	

	# put test media on all connected removable devices
	copy_testmedia_to_removable_devices()

	try:
		logger.info(f"Offloading data from all removable devices...")
		moved = offload_to(data_dir)
	except RuntimeError as e:
		logger.error(f"Failed to offload to {upload_dir}: {e}")


	try:
		change_sd_host_to_ext()
		logger.info(f"changed sd host to ext")
	except:
		logger.error(f"failed to change sd host to external")


	birdnet_prediction = config.get("birdnet-prediction", {})
	if birdnet_prediction.get("enabled", False):
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
	

	detect_speech = config.get("speech-detection", {})
	if detect_speech.get("enabled", False):
		logger.info("Speech detection enabled")
		try:
			results = mute(data_dir, margin_sec=0.25,debug=config.get("debug", False))
			for path, timestamps in results.items():
				logger.info(f"{path}: {len(timestamps)} speech segment(s)")
		except Exception as e:
			logger.error(f"Speech detection failed: {e}")
	else:
		logger.info("Speech detection disabled")
	
	logger.info("Transcoding files...")
	transcode(data_dir, config)
	

	if args.serve_port:
		logger.info(f"Starting web server on port {args.serve_port}...")
		server_thread = threading.Thread(target=serve_directory, args=(upload_dir, args.serve_port), daemon=True)
		server_thread.start()
		try:
			while True:
				time.sleep(1)
		except KeyboardInterrupt:
			logger.info("Stopping web server...")

	exit(0)

	logger.info("Uploading files...")
	storage = config.get('storage', {})
	provider = storage.get('provider')
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

	
	
	logger.info("Scheduling next alarm...")
	scheduler = config.get('scheduler', {})
	if scheduler.get('enabled'):
		interval = scheduler.get('interval_minutes')
		if interval is None or interval < 0:
			logger.warning(f"Invalid wake interval ({interval})")
		else:
			logger.info(f"Next wake alarm scheduled in {interval} minutes")
			set_wakealarm(interval)

	
	logger.info(f"Uptime: {time.time() - start_time:.2f} seconds")
	
	# time to die
	logger.info("Halting...")
	halt()
	exit(0)


