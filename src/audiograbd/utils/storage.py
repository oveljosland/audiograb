from abc import ABC, abstractmethod
from pathlib import Path
from google.cloud.storage import Client, transfer_manager
import logging

logger = logging.getLogger(__name__)



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

	def upload(self, src, workers=8):
		# get all files in `src` as Path objects
		directory_as_path_obj = Path(src)
		paths = directory_as_path_obj.rglob("*")

		# filter so the list only includes files, not directories
		file_paths = [path for path in paths if path.is_file()]

		# make paths relative to `src`
		relative_paths = [path.relative_to(src) for path in file_paths]

		# convert them to strings
		string_paths = [str(path) for path in relative_paths]

		logger.info("Found {} files.".format(len(string_paths)))

		results = transfer_manager.upload_many_from_filenames(
			self.bucket,
			string_paths,
			src=src,
			max_workers=workers,
		)

		"""
		Results list is either `None` or an exception
		for each filename in the input list, in order.
		"""
		for name, result in zip(string_paths, results):
			if isinstance(result, Exception):
				logger.error("Failed to upload {} due to exception: {}".format(name, result))
			else:
				logger.info("Uploaded {} to {}.".format(name, self.bucket.name))


class Sigma2Provider(StorageProvider):
	# TODO: implement class for Sigma2 provider
	pass
