from .decorators import ValidationSchema
from .schema import InputField


class DefaultRules:
	date = InputField.Date(regex="^\d{4}\-(0?[1-9]|1[012])\-(0?[1-9]|[12][0-9]|3[01])$")
	pk = InputField.String(required=True)
	gender = InputField.String(allowed=['M', 'F', 'O'])

	@staticmethod
	def pk_validation_rule(pk_name: str):
		return ValidationSchema(**{pk_name: InputField.String(required=True)})

	@staticmethod
	def search_validation_rule(fields: InputField.List = None, filters: InputField.Dictionary = None, **kwargs):
		return ValidationSchema(**{
			"fields": InputField.List(required=True) if not isinstance(fields, InputField.List) else fields,
			"filters": InputField.Dictionary(required=True) if not isinstance(filters, InputField.Dictionary) else filters,
			"limit": InputField.Integer(required=True, nullable=True),
			"offset": InputField.Integer(required=True, nullable=True),
			"order_by": InputField.String(required=False, nullable=True),
			"order_field": InputField.String(required=False, nullable=True),

		})
