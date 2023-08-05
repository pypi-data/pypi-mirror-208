from django.db.models import (TextField, BigAutoField)

from msb_cipher import Cipher


class EncryptedDatabaseField(TextField):
	description = "Encrypted Field Holds Private Data"
	_type = str

	def __init__(self, *args, **kwargs):
		kwargs['blank'] = True
		kwargs['null'] = True
		super().__init__(*args, **kwargs)

	def deconstruct(self):
		name, path, args, kwargs = super().deconstruct()
		del kwargs["blank"]
		del kwargs["null"]
		return name, path, args, kwargs

	def get_prep_value(self, value):
		return Cipher.encrypt(data=super().get_prep_value(value))

	def from_db_value(self, value, expression, connection):
		return Cipher.decrypt(data=value)

	def to_python(self, value):
		return self._type(Cipher.decrypt(data=value))


class EncryptedInteger(EncryptedDatabaseField):
	_type = int


class EncryptedString(EncryptedDatabaseField):
	_type = str


class EncryptedFloat(EncryptedDatabaseField):
	_type = float


class EncryptedBool(EncryptedDatabaseField):
	_type = bool


class EncryptedPrimaryKey(BigAutoField):
	def encrypted(self):
		return Cipher.encrypt(super(EncryptedPrimaryKey, self).get_prep_value(''))
