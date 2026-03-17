import mimetypes
import subprocess
from pathlib import Path




AUDIO_TRANSCODERS = {
	"opus": transcode_opus,
	"flac": transcode_flac
}



"""
TODO:
- Consider doing the transcoding in parallell. Found an example online:
	```
	from concurrent.futures import ProcessPoolExecutor
	from pathlib import Path
	import subprocess

	def transcode(path):
		subprocess.run([
			"ffmpeg", "-y", "-i", str(path),
			"-c:a", "flac", str(path.with_suffix(".flac"))
		], check=True)

	files = list(Path("audio").glob("*.mp3"))

	with ProcessPoolExecutor() as ex:
		ex.map(convert, files)
	```
"""

def skip(codec, ext):
	if codec == "opus" and ext == ".opus":
		return True
	if codec == "flac" and ext == ".flac":
		return True
	return False


def get_mime_type(path):
	"""
	Guess the MIME type of a file, returns
	`application/octet-stream` if it fails
	"""
	mime, _ = mimetypes.guess_type(path)
	return mime or "application/octet-stream"


def is_compressible(mime, config):
	if not config["transcoding"]["enabled"]:
		return False

	if mime.startswith("audio/"):
		return True

	return False




def remove_original(original: Path, output_path: Path):
	"""
	Used to remove the original file after succesful transcoding.
	"""
	if output_path.exists() and output_path != original:
		original.unlink(missing_ok=True)


def transcode_opus(input_path, config, debug=False):
	"""
	Transcode audio with FFmpeg.
	Get options from config, removes the original file afterwards.
	"""
	if not input_path.is_file():
		raise FileNotFoundError(input_path)

	if input_path.suffix.lower() == ".opus":
		return input_path

	output_path = input_path.with_suffix(".opus")

	cmd = [
		"ffmpeg",
		"-y",
		"-i",
		str(input_path),
		"-ac", "1", # mono
		"-ar", str(config["sample_rate"]),
		"-c:a", "libopus",
		"-b:a", f'{config["bitrate_kbps"]}k',
		str(output_path)
	]

	subprocess.run(
		cmd,
		check=True,
		stdout=None if debug else subprocess.DEVNULL,
		stderr=None if debug else subprocess.DEVNULL
	)
	
	remove_original(input_path, output_path)
	return output_path



def transcode(path, config, debug=False):
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

	if not is_compressible(mime, config):
		return path

	if mime.startswith("audio/"):
		return transcode_audio_opus(
			path,
			config["transcoding"]["audio"],
			debug=debug
		)

	return path
