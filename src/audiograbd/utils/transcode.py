import subprocess
from pathlib import Path


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


EXTENSIONS = {".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a", ".opus"}

TRANSCODERS = {
	"opus": transcode_opus,
	"flac": transcode_flac,
}

def skip(codec, ext):
	if codec == "opus" and ext == ".opus":
		return True
	if codec == "flac" and ext == ".flac":
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


def transcode_flac(input_path, config, debug=False):
	if not input_path.is_file():
		raise FileNotFoundError(input_path)

	if input_path.suffix.lower() == ".flac":
		return input_path

	output_path = input_path.with_suffix(".flac")

	cmd = [
		"ffmpeg",
		"-y",
		"-i", str(input_path),
		"-ac", "1", # mono
		"-c:a", "flac",
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
	path = Path(path)

	if path.is_dir():
		for file_path in path.rglob("*"):
			if file_path.is_file():
				transcode(file_path, config, debug=debug)
		return path

	if not config["transcoding"]["enabled"]:
		return path

	ext = path.suffix.lower()

	if ext not in EXTENSIONS:
		return path

	audio_config = config["transcoding"]["audio"]
	codec = audio_config["codec"]

	if skip(codec, ext):
		return path

	handler = TRANSCODERS.get(codec)
	if not handler:
		raise ValueError(f"unsupported codec: {codec}")

	return handler(path, audio_config, debug=debug)