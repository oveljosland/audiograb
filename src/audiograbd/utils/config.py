import os
import json
from pathlib import Path # TODO: maybe use this for the other modules too ...

try:
	import requests
except ImportError:
	requests = None



CACHE_DIR = Path("~/.config/audiograb/").expanduser()

CACHED_CONFIG = CACHE_DIR / "config.json"
REMOTE_CONFIG = "https://folk.ntnu.no/ovelj/config.json"
BACKUP_CONFIG = "src/config/example.json"



def make_cache_dir():
	"""Make the cache directory."""
	CACHE_DIR.mkdir(parents=True, exist_ok=True)



def download_config(url, timeout=10):
	"""Download config file from URL."""
	if requests is None:
		print("Missing `requests`")
		return None
	
	try:
		response = requests.get(url, timeout=timeout)
		response.raise_for_status()
		config = response.json()
		print(f"downloaded config from {url}")
		return config
	except requests.exceptions.RequestException as e:
		print(f"failed to download config from {url}: {e}")
		return None
	except json.JSONDecodeError as e:
		print(f"Invalid JSON in config: {e}")
		return None



def cache_config(config):
	"""Cache the config file in `CACHE_DIR`."""
	try:
		make_cache_dir()
		with open(CACHED_CONFIG, "w") as cache:
			json.dump(config, cache, indent=4)
		print(f"cached config to {CACHED_CONFIG}")
		return True
	except Exception as e:
		print(f"failed to cache config: {e}")
		return False



def load_cached():
	"""Load the cached configuration file."""
	if not CACHED_CONFIG.exists():
		print(f"cached config not found: {CACHED_CONFIG}")
		return None
	
	try:
		with open(CACHED_CONFIG, "r") as cache:
			config = json.load(cache)
		print(f"loaded cached config: {CACHED_CONFIG}")
		return config
	except Exception as e:
		print(f"failed load cached config: {e}")
		return None



def load_backup(path=BACKUP_CONFIG):
	"""Load the backup configuration file included in this repository."""
	if not os.path.exists(path):
		print(f"backup config not found: {path}")
		return None
	
	try:
		with open(path, "r") as backup:
			config = json.load(backup)
		print(f"loaded backup config: {path}")
		return config
	except Exception as e:
		print(f"failed load backup config: {e}")
		return None



def load_config(url=REMOTE_CONFIG, cache=True):
	"""Load the config file.
	
	Priority
	1. Remote
	2. Cached
	3. Backup
	"""

	print(f"trying to download config from {url}")
	config = download_config(url)

	if config is not None:
		if cache:
			cache_config(config)
		print("using remote config")
		return config
	
	print(f"failed to download config")

	config = load_cached()
	if config is not None:
		print("using cached config")
		return config
	
	print(f"failed to load cached config")

	config = load_backup()
	if config is not None:
		print("using backup config")
		return config
	
	raise RuntimeError(
		f"\nfailed to load config from any of the following sources:\n"
		f"\tremote: {url}\n"
		f"\tcached: {CACHED_CONFIG}\n"
		f"\tbackup: {BACKUP_CONFIG}\n"
	)


