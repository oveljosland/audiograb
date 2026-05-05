import subprocess
import logging
from pathlib import Path
from silero_vad import load_silero_vad, read_audio, get_speech_timestamps
from audiograbd.utils.transcode import EXTENSIONS

logger = logging.getLogger(__name__)



def get_timestamps(path, model=None):
	"""Return speech timestamps for a file or directory."""
	path = Path(path)

	if path.is_dir():
		results = {}
		for file_path in sorted(path.rglob("*")):
			if file_path.suffix.lower() not in EXTENSIONS:
				continue
			results[str(file_path)] = get_timestamps(file_path, model=model)
		return results

	if model is None:
		model = load_silero_vad()

	wav = read_audio(str(path))
	return get_speech_timestamps(
		wav,
		model,
		return_seconds=True, # False: samples
	)



def build_mute_filter(timestamps, margin_sec=None):
	"""Build the FFmpeg enable expression for muting the speech segments.
	Optionally add a margin before and after each segment."""
	if not timestamps:
		return None

	expressions = []
	margin = margin_sec if margin_sec is not None else 0.0

	for segment in timestamps:
		start = float(segment["start"] - margin)
		end = float(segment["end"] + margin)
		expressions.append(f"between(t,{start:.3f},{end:.3f})")
	return "+".join(expressions)



def mute_speech_segments(path, timestamps, margin_sec=None, debug=False):
	"""Mute speech segments using FFmpeg."""
	path = Path(path)

	if not timestamps:
		return path

	expression = build_mute_filter(timestamps, margin_sec=margin_sec)
	if not expression:
		return path

	# input : audio.wav
	# output: audio.muted.wav
	output_path = path.with_name(f"{path.stem}.muted{path.suffix}")
	cmd = [
		"ffmpeg",
		"-y",
		"-i",
		str(path),
		"-af",
		f"volume=enable='{expression}':volume=0",
		str(output_path),
	]

	subprocess.run(
		cmd,
		check=True,
		stdout=None if debug else subprocess.DEVNULL,
		stderr=None if debug else subprocess.DEVNULL,
	)

	output_path.replace(path) # replace file with the muted one
	return path



def mute(path, model=None, margin_sec=None, debug=False):
	"""Detect speech segments in audio files and mute them."""
	path = Path(path)
	if model is None:
		model = load_silero_vad()

	if path.is_dir():
		results = {}
		for file_path in sorted(path.rglob("*")):
			if file_path.suffix.lower() not in EXTENSIONS:
				continue
			try:
				timestamps = get_timestamps(file_path, model=model)
				if timestamps:
					mute_speech_segments(file_path, timestamps, margin_sec=margin_sec, debug=debug)
				results[str(file_path)] = timestamps
			except Exception as e:
				logger.warning(f"Skipping corrupted/unrecognised file {file_path}: {e}")
				"""TODO: decide to skip or delete the file"""
				# path.unlink(missing_ok=True)
		return results

	try:
		timestamps = get_timestamps(path, model=model)
		if timestamps:
			mute_speech_segments(path, timestamps, margin_sec=margin_sec, debug=debug)
		return timestamps
	except Exception as e:
		logger.warning(f"Skipping corrupted/unrecognised file {path}: {e}")
		"""TODO: decide to skip or delete the file"""
		# path.unlink(missing_ok=True)
		return []
