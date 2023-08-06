from django.db import models

from .model_fields import EncryptedString
from .msb_model import MsbModel
from .msb_model import MsbModelManager


class ConfigurationModelManager(MsbModelManager):

	def get_config(self, name: str, map_to=None):
		_config_list = []
		try:
			_config_list = self.get_queryset().filter(name=name).all()
		except Exception:
			pass
		return map_to(*_config_list) if callable(map_to) else _config_list


# Configuration model
class Configuration(MsbModel):
	_list_field_names = ["name", "label", "value"]
	_identifier_field = "name"

	# meta data
	class Meta:
		abstract = True
		indexes = [models.Index(fields=['name', 'key'])]
		unique_together = ("name", "key")

	# Model fields
	name = models.CharField(max_length=100, db_column='name')
	key = models.CharField(max_length=255, db_column='key')
	value = EncryptedString(db_column='value')
	label = models.CharField(max_length=255, db_column='label', null=True)
	field_type = models.CharField(max_length=255, db_column='field_type', null=True)

	# assign a custom manager to the model
	objects = ConfigurationModelManager()

	def __str__(self):
		return f"<{self.__class__.__name__} [{self.name}]: {self.key}>"
