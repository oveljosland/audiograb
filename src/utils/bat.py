import subprocess

def get_voltage():
	output = subprocess.run([
		"vcgencmd", "pmic_read_adc", "BATT_V"
		],
		capture_output=True,
		check=True,
		text=True
	)
	output = output.stdout.strip()
	output = output.split("=")[1].removesuffix('V')
	return output
