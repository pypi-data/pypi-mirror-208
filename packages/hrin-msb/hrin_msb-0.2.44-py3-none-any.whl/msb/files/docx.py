import os
from pathlib import Path

from pdf2docx import Converter

from .core import FileExceptions
from .core import FileInterface, FileBase
from .core import FileMessage
from .core import GeneratedFile
from .pdf import PdfFile


class DocxFile(FileBase, FileInterface):
	_extension = None

	def __init__(self):
		self._extension = ".docx"

	def save(self, filename: str, location: str) -> GeneratedFile:
		file = GeneratedFile()
		try:
			content = self.content
			doc_filepath = os.path.join(location, filename + self._extension)
			Path(location).mkdir(parents=True, exist_ok=True)
			if os.path.exists(doc_filepath) and self.file_overwrite is False:
				raise FileExceptions.DocxExistsException
			"""Generate PDF"""
			pdf = PdfFile().set_content(content)
			if self.file_overwrite is True:
				pdf.set_file_overwrite()
			generated_pdf = pdf.save(location=location, filename=filename)
			pdf_path = generated_pdf.path

			if pdf_path != "":
				"""Generate docx file"""
				cv = Converter(pdf_path)
				cv.convert(doc_filepath)
				cv.close()
				if not cv:
					FileExceptions.DocxException()
				else:
					file.path = doc_filepath
					file.message = FileMessage.doc()
					os.remove(pdf_path)
			else:
				raise FileExceptions.PdfException()
		except Exception as e:
			file.message = e
			file.error = True
		finally:
			return file
