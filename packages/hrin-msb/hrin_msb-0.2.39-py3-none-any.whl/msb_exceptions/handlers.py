import logging


class CustomExceptionHandler:

	@staticmethod
	def handle_exception(e):
		return CustomExceptionHandler.handle_error(e)
		logging.exception(e)

	@staticmethod
	def handle_error(e):
		logging.error(f"Error : {e}")
