from django.db import models

from msb_cipher import Cipher
from .constants import (COLUMN_NAME_DELETED)


class MsbModelManager(models.Manager):
	_default_filters = {}

	def _get_filtered_queryset(self, **filters):
		_query_set = super(MsbModelManager, self).get_queryset()
		query_filters = {}
		for filtername, filtervalue in filters.items():
			if hasattr(self.model, filtername):
				query_filters[filtername] = filtervalue
		return _query_set.filter(**query_filters)

	def get(self, *args, **kwargs):
		filters = {**kwargs}
		pk = kwargs.get('pk')
		if pk is not None and isinstance(pk, str):
			filters['pk'] = int(Cipher.decrypt(pk))
		return super(MsbModelManager, self).get(*args, **filters)

	@property
	def deleted(self):
		return self._get_filtered_queryset(**{COLUMN_NAME_DELETED: True})

	def get_queryset(self):
		return self._get_filtered_queryset(**{COLUMN_NAME_DELETED: False, **self._default_filters})
