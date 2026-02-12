import mimetypes
import os
import subprocess
from PIL import Image

IGNORE_IMAGE_TYPES = {
	"image/jpeg",
	"image/webp"
}

IGNORE_AUDIO_TYPES = {
	"audio/mpeg",
	"audio/opus",
	"audio/aac"
}

IGNORE_VIDEO_TYPES = {
	"video/mp4"
}

def get_mime_type(path):
	mime, _ = mimetypes.guess_type(path)
	return mime or "application/octet-stream"


def is_compressible(path, mime, config):
	if not config["compression"]["enabled"]:
		return False
	
	if config["compression"].get("skip_already_compressed", True):
		if mime.startswith("image/") and mime in IGNORE_IMAGE_TYPES:
			return False
		if mime.startswith("audio/") and mime in IGNORE_AUDIO_TYPES:
			return False
		if mime.startswith("video/") and mime in IGNORE_VIDEO_TYPES:
			return False
	return True

# TODO: include other formats/codecs
# this is jsut for testing

"""
TODO:
- consider more descriptive return values for these routines?
"""

def compress_audio_opus(input_path, config):
	if not os.path.isfile(input_path):
		raise FileNotFoundError(input_path)

	base, ext = os.path.splitext(input_path)
	if ext.lower() == ".opus":
		return input_path

	output_path = base + ".opus"

	cmd = [
		"ffmpeg",
		"-y",
		"-i",
		input_path,
		"-ac",
		"1",
		"-ar",
		str(config["sample_rate"]),
		"-c:a",
		"libopus",
		"-b:a",
		f'{config["bitrate_kbps"]}k',
		output_path
	]

	subprocess.run(cmd, check=True)
	return output_path


def compress_image_jpeg(input_path, config):
	image = Image.open(input_path)
	image.thumbnail((config["max_width"], config["max_height"]))

	base, _ = os.path.splitext(input_path)
	output_path = base + ".jpg"

	image.save(
		output_path,
		format="JPEG",
		quality=config["jpeg_quality"],
		optimize=True
	)

	return output_path


def compress_if_needed(path, config):
	mime = get_mime_type(path)

	if not is_compressible(path, mime, config):
		return path

	if mime.startswith("audio/"):
		return compress_audio_opus(path, config["compression"]["audio"])
	
	if mime.startswith("image/"):
		return compress_image_jpeg(path, config["compression"]["image"])
	
	"""
	if mime.startswith("video/"):
		return compress_video_mkv(path, config["compression"]["video"])
	"""

	return path
