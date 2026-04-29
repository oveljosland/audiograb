import os
import json
import logging
from pathlib import Path # TODO: maybe use this for the other modules too ...

try:
	import requests
except ImportError:
	requests = None

logger = logging.getLogger(__name__)



CACHE_DIR = Path("~/.config/audiograb/").expanduser()

CACHED_CONFIG = CACHE_DIR / "config.json"
REMOTE_CONFIG = "https://folk.ntnu.no/ovelj/config.json"
BACKUP_CONFIG = "src/config/example.json" # double check this path



def make_cache_dir():
	"""Make the cache directory."""
	CACHE_DIR.mkdir(parents=True, exist_ok=True)



def download_config(url, timeout=10):
	"""Download config file from URL."""
	if requests is None:
		logger.error("Missing module `requests`")
		return None
	
	try:
		response = requests.get(url, timeout=timeout)
		response.raise_for_status()
		config = response.json()
		logger.info(f"Downloaded config from {url}")
		return config
	except requests.exceptions.RequestException as e:
		logger.error(f"Failed to download config from {url}: {e}")
		return None
	except json.JSONDecodeError as e:
		logger.error(f"Invalid JSON in config: {e}")
		return None



def cache_config(config):
	"""Cache the config file in `CACHE_DIR`."""
	try:
		make_cache_dir()
		with open(CACHED_CONFIG, "w") as cache:
			json.dump(config, cache, indent=4)
		logger.info(f"Config cached to {CACHED_CONFIG}")
		return True
	except Exception as e:
		logger.error(f"Failed to cache config: {e}")
		return False



def load_cached():
	"""Load the cached configuration file."""
	if not CACHED_CONFIG.exists():
		logger.warning(f"cached config not found: {CACHED_CONFIG}")
		return None
	
	try:
		with open(CACHED_CONFIG, "r") as cache:
			config = json.load(cache)
		logger.info(f"Loaded cached config: {CACHED_CONFIG}")
		return config
	except Exception as e:
		logger.error(f"Failed to load cached config: {e}")
		return None



def load_backup(path=BACKUP_CONFIG):
	"""Load the backup configuration file included in this repository."""
	if not os.path.exists(path):
		logger.warning(f"Backup config not found: {path}")
		return None
	
	try:
		with open(path, "r") as backup:
			config = json.load(backup)
		logger.info(f"Loaded backup config: {path}")
		return config
	except Exception as e:
		logger.error(f"Failed to load backup config: {e}")
		return None



def load_config(url=REMOTE_CONFIG, cache=True, force_backup=False):
	"""Load the config file.
	
	Priority
	1. Remote
	2. Cached
	3. Backup
	"""

	if force_backup:
		return load_backup()


	logger.info(f"trying to download config from {url}")
	config = download_config(url)

	if config is not None:
		if cache:
			cache_config(config)
		logger.info("using remote config")
		return config
	
	logger.warning("Failed to download config")

	config = load_cached()
	if config is not None:
		logger.info("Using cached config")
		return config
	
	logger.warning("Failed to load cached config")

	config = load_backup()
	if config is not None:
		logger.info("Using backup config")
		return config
	
	raise RuntimeError(
		f"\nFailed to load config from any of the following sources:\n"
		f"\tremote: {url}\n"
		f"\tcached: {CACHED_CONFIG}\n"
		f"\tbackup: {BACKUP_CONFIG}\n"
	)


