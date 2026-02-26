# codnig loader. downloads config from a remote server, caches it,
# and falls back to cache or local file if download failss

import os
import json
from pathlib import Path # TDOD: maybe use this for the other modules too ...

# in case requirements were not installed
try:
	import requests
except ImportError:
	requests = None


CACHE_DIR = Path("/tmp/.audiograb_config")

CACHED_CONFIG = CACHE_DIR / "config.json"
REMOTE_CONFIG = "https://folk.ntnu.no/ovelj/config.json" # free real estate
BACKUP_CONFIG = "src/config/example.json" # fallback

def make_cache_dir():
	CACHE_DIR.mkdir(parents=True, exist_ok=True)

def download_config(url, timeout=10):
	if requests is None:
		print("requests is NONE")
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
		print(f"invalid json in remote config: {e}")
		return None



def cache_config(config):
	"""
	cache config file
	"""
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
	"""
	load cached config file
	"""
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

def load_fallback(path=BACKUP_CONFIG):
	"""
	load fallback config
	"""
	if not os.path.exists(path):
		print(f"fallback config not found: {path}")
		return None
	
	try:
		with open(path, "r") as fallback:
			config = json.load(fallback)
		print(f"loaded fallback config: {path}")
		return config
	except Exception as e:
		print(f"failed load fallback config: {e}")
		return None

def load_config(url=REMOTE_CONFIG, cache=True):
	# priority
	# 1. url
	# 2. cache
	# 3. fallback

	print(f"trying to download config from {url}")
	config = download_config(url)

	if config is not None:
		if cache:
			cache_config(config)
		print("using downloaded config")
		return config
	
	print(f"failed to download config")

	config = load_cached()
	if config is not None:
		print("using cached config")
		return config
	
	print(f"failed to load cached config")

	config = load_fallback()
	if config is not None:
		print("using fallback config")
		return config
	
	raise RuntimeError(
		f"\nfailed to load config from any of the following sources:\n"
		f"\tremote:   {url}\n"
		f"\tcache:    {CACHED_CONFIG}\n"
		f"\tfallback: {BACKUP_CONFIG}\n"
	)

