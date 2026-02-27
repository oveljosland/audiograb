from abc import ABC, abstractmethod

from google.cloud import storage

class StorageProvider(ABC):
	@abstractmethod
	def upload(self, local_path, remote_path):
		pass
