from abc import ABC, abstractmethod
from pathlib import Path
from google.cloud.storage import Client, transfer_manager
import subprocess


# https://www.geeksforgeeks.org/python/abstract-classes-in-python/
# https://docs.cloud.google.com/storage/docs/samples?language=python

class StorageProvider(ABC):
	@abstractmethod
	def upload(self, local_path, **kwargs):
		"""
		concrete implementations may accept keywords that are specific
		to the provider, e.g. `workers` for GCS.
		"""
		pass

class GCSProvider(StorageProvider):
	def __init__(self, bucket_name):
		self.client = Client()
		self.bucket = self.client.bucket(bucket_name)

	def upload(self, source_directory, workers=8):
		# get all files in `source_directory` as Path objects
		directory_as_path_obj = Path(source_directory)
		paths = directory_as_path_obj.rglob("*")

		# filter so the list only includes files, not directories
		file_paths = [path for path in paths if path.is_file()]

		# make paths relative to `source_directory`
		relative_paths = [path.relative_to(source_directory) for path in file_paths]

		# convert them to strings
		string_paths = [str(path) for path in relative_paths]

		print("found {} files.".format(len(string_paths)))

		results = transfer_manager.upload_many_from_filenames(
			self.bucket,
			string_paths,
			source_directory=source_directory,
			max_workers=workers,
		)

		"""
		results list is either `None` or an exception
		for each filename in the input list, in order.
		"""
		for name, result in zip(string_paths, results):
			if isinstance(result, Exception):
				print("failed to upload {} due to exception: {}".format(name, result))
			else:
				print("uploaded {} to {}.".format(name, self.bucket.name))


class Sigma2Provider(StorageProvider):
	
	def __init__(self, cred_path="/home/jonas/folder/NIRD_credentials/ove_creds.txt"):
		self.cred_path = cred_path #given that file is formated username,password
		self.credentials = open(cred_path, "r").read().split(",") 

	def upload(self, source_directory, username, port=12 ):
		output = subprocess.run(["scp", "-P", str(port), source_directory,
		username + "@login.nird.sigma2.no:folder/"], check=True, capture_output=True) #use -P12 port 12 to avoid firewall at nird (or something)
		if output.returncode != 0:
			print("Failed to upload to NIRD. SSH ERROR:", output.returncode)