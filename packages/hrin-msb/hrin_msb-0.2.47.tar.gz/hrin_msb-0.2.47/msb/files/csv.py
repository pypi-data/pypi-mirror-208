import os
from pathlib import Path

import pandas as pd

from .core import FileExceptions
from .core import FileInterface, FileBase
from .core import FileMessage
from .core import GeneratedFile


class CsvFile(FileBase, FileInterface):
	content: list = list()
	_extension = ".csv"

	def __init__(self):
		self._extension = ".csv"

	def set_content(self, content: list):
		self.content = content
		return self

	def save(self, filename: str, location: str) -> GeneratedFile:
		file = GeneratedFile()
		try:
			filename = filename
			content = self.content
			filepath = os.path.join(location, filename + self._extension)

			if os.path.exists(filepath) and self.file_overwrite is False:
				raise FileExceptions.CsvException

			Path(location).mkdir(parents=True, exist_ok=True)
			dataframe = pd.DataFrame(content)
			dataframe.to_csv(filepath, index=False)
			file.path = filepath
			file.message = FileMessage.csv()
		except Exception as e:
			file.message = e
			file.error = True
		finally:
			return file
