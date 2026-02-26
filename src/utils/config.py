# codnig loader. downloads config from a remote server, caches it,
# and falls back to cache or local file if download failss

import os
import json
import requests
from pathlib import Path # TDOD: maybe use this for the other modules too ...

CACHE_DIR = Path("/tmp/.audiograb_config")

CACHED_CONFIG = CACHE_DIR / "config.json"
REMOTE_CONFIG = "https://folk.ntnu.no/ovelj/config.json" # free real estate
BACKUP_CONFIG = "src/config/example.json" # fallback

