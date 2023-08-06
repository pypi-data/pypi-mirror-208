from django.conf import settings
from django.core.serializers import serialize
from django.db import models as Models
from msb.cipher import Cipher
from msb.env.constants import MsbConfigNames as _mcn

from .constants import (COLUMN_NAME_DELETED, COLUMN_NAME_DELETED_BY)
from .msb_model_manager import MsbModelManager


class MsbModel(Models.Model):
	_private_fields: list = []
	_list_field_names: list = []
	_identifier_field: str = ""
	_encrypt_private_fields: bool = getattr(settings, _mcn.MSB_DB_ENCRYPT_PRIVATE_FIELDS, False)
	_pk_is_private_fields: bool = getattr(settings, _mcn.MSB_DB_PK_IS_PRIVATE_FIELD, False)
	_hidden_fields: list = []

	class Meta:
		abstract = True

	@property
	def secure_fields(self):
		_secure_fields = self._private_fields if isinstance(self._private_fields, list) else []
		if self._pk_is_private_fields:
			_secure_fields.append(self._meta.pk.attname)
		return _secure_fields

	@property
	def identifier_field_name(self):
		if isinstance(self._identifier_field, str) and len(self._identifier_field) > 0:
			return self._identifier_field
		return ''

	def _get_field_value(self, field_name: str, encrypt: bool = False, default=None):
		try:
			if "." in field_name:
				field_name, relation_name, *_ = field_name.split(".")
				local_field_value = getattr(self, field_name, None)
				field_value = local_field_value._get_field_value(relation_name, default=None)
			else:
				field_value = getattr(self, field_name, default)
				if isinstance(field_value, MsbModel):
					field_value = field_value._get_field_value(field_value.pk_name)

		except Exception as e:
			field_value = None
		finally:

			if (field_name in self.secure_fields) and (encrypt or self._encrypt_private_fields):
				return Cipher.encrypt(field_value)
			return field_value

	@property
	def related_fields(self):
		fields = []
		for field in self._meta.fields:
			if field.get_internal_type() in ['ForeignKey']:
				fields.append(field.name)
		return fields

	@property
	def pk_name(self):
		return self._meta.pk.attname

	@property
	def pk_value(self):
		return getattr(self, self.pk_name) if self.pk_name is not None else ""

	@property
	def identifier(self):
		return f"{getattr(self, self.identifier_field_name)}" if hasattr(self, self.identifier_field_name) else ""

	@property
	def list_field_names(self) -> list:
		return [self.pk_name, *self._list_field_names] if isinstance(self._list_field_names, list) else None

	def dict(self, encrypted: bool = False):
		encrypted = encrypted or self._encrypt_private_fields
		try:
			return {
				k: v if (k not in self.secure_fields or not encrypted) else Cipher.encrypt(v)
				for k, v in super().__dict__.items()
				if not k.startswith('__') and not k.startswith('_') and not callable(k)
				   and k not in self._hidden_fields
			}

		except Exception:
			return dict()

	@property
	def list_fields(self) -> dict:
		if len(self.list_field_names) > 0:
			return {field_name.replace('.', '_'): self._get_field_value(field_name) for field_name in self.list_field_names}
		return None

	@property
	def serialized(self):
		return serialize('python', [self])

	def delete(self, deleted_by=None, using=None, keep_parents=False):
		if hasattr(self, COLUMN_NAME_DELETED):
			setattr(self, COLUMN_NAME_DELETED, True)

		if hasattr(self, COLUMN_NAME_DELETED_BY):
			setattr(self, COLUMN_NAME_DELETED_BY, deleted_by)
		self.save()
		return True

	def recover(self):
		if hasattr(self, COLUMN_NAME_DELETED):
			setattr(self, COLUMN_NAME_DELETED, False)
		self.save()
		return True

	def __str__(self):
		return f"<{self.__class__.__name__} [{self.pk_value}]: {self.identifier}>"

	def __unicode__(self):
		return self.__str__()

	def __repr__(self):
		return self.__str__()

	@property
	def rows(self):
		return self.objects

	objects = MsbModelManager()
