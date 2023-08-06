from .csv import CsvFile
from .docx import DocxFile
from .pdf import PdfFile


class FileFactory:

	@staticmethod
	def create_pdf_file() -> PdfFile:
		return PdfFile()

	@staticmethod
	def create_csv_file() -> CsvFile:
		return CsvFile()

	@staticmethod
	def create_docx_file() -> DocxFile:
		return DocxFile()
