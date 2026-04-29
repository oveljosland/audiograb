from silero_vad import load_silero_vad, read_audio, get_speech_timestamps



def get_timestamps(path):
	model = load_silero_vad()
	wav = read_audio(path)
	timestamps = get_speech_timestamps(
		wav,
		model,
		return_seconds=True, # False: return samples
	)
	return timestamps