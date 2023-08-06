from msb.env.constants import NameConst
from rest_framework.request import Request
from rest_framework.views import APIView
from .exceptions import (ValidationExceptions)
from .schema import ValidationSchema


def parse_payload_from_request(request: Request):
	try:
		_payload = request.data
		return _payload
	except Exception as e:
		raise ValidationExceptions.InvalidPayloadFormat


def parse_schema_and_inp_for_bulk_validation(schema: ValidationSchema, inp, bulk=False):
	_parsed_schema = schema.parsed_schema
	_parsed_inp = inp
	if bulk:
		_parsed_schema = {NameConst.BULK_SCHEMA_NAME: {'type': 'list', 'schema': {'type': 'dict', 'schema': _parsed_schema}}}
		_parsed_inp = {NameConst.BULK_SCHEMA_NAME: inp}

	return _parsed_schema, _parsed_inp


def format_list_errors_to_string(errors: dict):
	return {k: v[0] if isinstance(v, list) and len(v) > 0 else v for k, v in errors.items()}


def formatted_validation_errors(errors: dict, bulk: bool = False):
	if isinstance(errors, dict) and len(errors.keys()) > 0:
		try:
			if bulk:
				error_list: dict = errors.get(NameConst.BULK_SCHEMA_NAME)[0]
				for error_index, errors in error_list.items():
					error_list.update({error_index: format_list_errors_to_string(errors=errors[0])})
				return error_list
			else:
				return format_list_errors_to_string(errors=errors)

		except Exception:
			raise ValidationExceptions.ErrorFormattingFailed
	return None


def validate_against(schema: ValidationSchema = None, inp=None, unknown=False, bulk: bool = False):
	if not isinstance(schema, ValidationSchema):
		raise ValidationExceptions.InvalidValidationSchema

	if not ((bulk and isinstance(inp, list)) or (not bulk and isinstance(inp, dict))):
		raise ValidationExceptions.InvalidValidationInput

	errors = {}
	schema, inp = parse_schema_and_inp_for_bulk_validation(schema, inp, bulk=bulk)
	try:
		from cerberus.validator import Validator
		_validator = Validator(schema, allow_unknown=unknown)
		_validator.validate(inp)
		errors = _validator.errors
	except Exception as e:
		raise ValidationExceptions.ValidationFailed
	return formatted_validation_errors(errors, bulk=bulk)


def validate_inp_payload(schema: ValidationSchema, request: Request, allow_unknown: bool, bulk_inp: bool):
	"""
		validate paload data if payload rules are defined
	"""
	_payload = parse_payload_from_request(request=request)
	payload_validation_errors = validate_against(
		schema=schema, inp=_payload, unknown=allow_unknown, bulk=bulk_inp
	)
	if payload_validation_errors:
		raise ValidationExceptions.InvalidPayloadException(errors=payload_validation_errors)


def validate_inp_parameters(schema: ValidationSchema, params: dict, allow_unknown: bool):
	"""
		validate paramerer data if payload rules are defined
	"""
	params_validation_errors = validate_against(schema=schema, inp=params, unknown=allow_unknown)
	if params_validation_errors:
		raise ValidationExceptions.InvalidParamsException(errors=params_validation_errors)



