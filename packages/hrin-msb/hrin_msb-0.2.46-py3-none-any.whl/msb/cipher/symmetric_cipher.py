import os

from cryptography.fernet import Fernet


class SymmetricCipher():

	def __init__(self, keyname: str = "SECRET_KEY", key: str = None):
		self.key = os.environ.get('SECRET_KEY', default='')

	def encrypt(self, data=None) -> str:
		if self.key is not None:
			try:
				data = str(data).encode() if not isinstance(data, bytes) else data
				return Fernet(key=self.key).encrypt(data).decode()
			except Exception as e:
				pass

		return data

	def decrypt(self, data=None) -> str:
		if self.key is not None:
			try:
				if isinstance(data, bytes):
					data = str(data).encode()
				return Fernet(key=self.key).decrypt(data).decode()
			except Exception:
				pass
		return data
