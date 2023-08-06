import os
from io import BytesIO
from pathlib import Path

from xhtml2pdf import pisa

from .core import FileExceptions
from .core import FileInterface, FileBase
from .core import FileMessage
from .core import GeneratedFile


class PdfFile(FileBase, FileInterface):
	_extension = None

	def __init__(self):
		self._extension = ".pdf"

	def save(self, filename: str, location: str) -> GeneratedFile:
		file = GeneratedFile()
		try:
			filepath = os.path.join(location, filename + self._extension)
			if os.path.exists(filepath) and self.file_overwrite is False:
				raise FileExceptions.PdfExistsException
			Path(location).mkdir(parents=True, exist_ok=True)
			with open(filepath, 'wb+') as output:
				content = self.content
				pdf = pisa.pisaDocument(BytesIO(content.encode("ISO-8859-1")), output)
				if not pdf.err:
					file.path = filepath
					file.message = FileMessage.pdf()
				else:
					raise FileExceptions.PdfException
		except Exception as e:
			file.message = e
			file.error = True
		finally:
			return file
