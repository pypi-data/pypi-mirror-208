from django.db import models

from .constants import (
	COLUMN_NAME_DELETED, COLUMN_NAME_CREATED_AT, COLUMN_NAME_UPDATED_AT,
	COLUMN_NAME_CREATED_BY, COLUMN_NAME_UPDATED_BY
)
from .msb_model import MsbModel


class MsbModelMetaFields(MsbModel):
	class Meta:
		abstract = True

	updated_at = models.DateTimeField(db_column=COLUMN_NAME_UPDATED_AT, auto_now=True)
	updated_by = models.IntegerField(db_column=COLUMN_NAME_UPDATED_BY, null=True, default=None)
	created_at = models.DateTimeField(db_column=COLUMN_NAME_CREATED_AT, auto_now_add=True)
	created_by = models.IntegerField(db_column=COLUMN_NAME_CREATED_BY, null=True, default=None)
	is_deleted = models.BooleanField(db_column=COLUMN_NAME_DELETED, default=False, null=False)
