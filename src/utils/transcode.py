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

def remove_original(original, output_path):
	"""
	Used to remove the original file after succesful transcoding.
	"""
	if os.path.isfile(output_path) and output_path != original:
		try:
			os.remove(original)
		except OSError:
			pass
	return output_path



def transcode_audio_opus(input_path, config):
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
	remove_original(input_path, output_path)
	return output_path


def transcode_image_jpeg(input_path, config):
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
	remove_original(input_path, output_path)
	return output_path


def transcode(path, config,):
	"""
	Transcode a file or directory if determined by `config'.
	This routine can be called with either a single file path or a
	directory. If given a directory it will walk the tree and try to
	transcode audio, video, and images to the formats specified in `config'.

	For files, the return value is the path to the converted file,
	or the original path if no transcoding was performed.
	
	The original files are removed after transcoding them.

	For directories, the return value is the original directory path.
	"""

	if os.path.isdir(path):
		for root, _, files in os.walk(path):
			for file_name in files:
				file_path = os.path.join(root, file_name)
				transcode(file_path, config)
		return path

	mime = get_mime_type(path)

	if not is_compressible(path, mime, config):
		return path

	if mime.startswith("audio/"):
		return transcode_audio_opus(path, config["compression"]["audio"])

	if mime.startswith("image/"):
		return transcode_image_jpeg(path, config["compression"]["image"])

	"""
	if mime.startswith("video/"):
		return transcode_video_mkv(path, config["compression"]["video"])
	"""

	return path
