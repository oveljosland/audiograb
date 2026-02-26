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