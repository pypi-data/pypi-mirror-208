from abc import ABC, abstractmethod

from .dataclasses import GeneratedFile


class FileInterface(ABC):
	"""Save Function will generate the file to the path given during function call"""

	@abstractmethod
	def save(self, filename: str, location: str) -> GeneratedFile:
		pass

	"""set_content() Function will store the content values that will used to save within the file"""

	@abstractmethod
	def set_content(self, content: str):
		pass

	"""set_file_overwrite() Function will be used if someone want to overwrite the existed file"""

	@abstractmethod
	def set_file_overwrite(self):
		pass

	@abstractmethod
	def set_protection(self):
		pass


class FileBase:
	content: str = None
	file_overwrite: bool = False

	def set_content(self, content: str):
		self.content = content
		return self

	def set_file_overwrite(self):
		self.file_overwrite = True
		return self

	def set_protection(self):
		return self
