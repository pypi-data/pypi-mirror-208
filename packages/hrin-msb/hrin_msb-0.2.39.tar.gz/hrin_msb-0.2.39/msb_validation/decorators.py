from functools import wraps

from rest_framework import request as drf_request

from msb_http import ApiResponse
from .exceptions import (ValidatorExceptions, InvalidPayloadFormat, InvalidPayloadException, InvalidParamsException)
from .schema import ValidationSchema

BULK_SCHEMA_NAME = 'schema_list'


def __parse_payload_from_request(request: drf_request.Request):
	try:
		_payload = request.data
		return _payload
	except Exception as e:
		raise InvalidPayloadFormat


def __parse_schema_and_inp_for_bulk_validation(schema: ValidationSchema, inp, bulk=False):
	_parsed_schema = schema.parsed_schema
	_parsed_inp = inp
	if bulk:
		_parsed_schema = {BULK_SCHEMA_NAME: {'type': 'list', 'schema': {'type': 'dict', 'schema': _parsed_schema}}}
		_parsed_inp = {BULK_SCHEMA_NAME: inp}

	return _parsed_schema, _parsed_inp


def __format_list_errors_to_string(errors: dict):
	return {k: v[0] if isinstance(v, list) and len(v) > 0 else v for k, v in errors.items()}


def __formatted_validation_errors(errors: dict, bulk: bool = False):
	if isinstance(errors, dict) and len(errors.keys()) > 0:
		try:
			if bulk:
				error_list: dict = errors.get(BULK_SCHEMA_NAME)[0]
				for error_index, errors in error_list.items():
					error_list.update({error_index: __format_list_errors_to_string(errors=errors[0])})
				return error_list
			else:
				return __format_list_errors_to_string(errors=errors)

		except Exception:
			raise ValidatorExceptions.ErrorFormattingFailed
	return None


def validation_schema_wrapper(klass):
	def get(key: str, default=None) -> ValidationSchema | None:
		if hasattr(klass, key) and isinstance((schema := getattr(klass, key)), ValidationSchema):
			return schema
		return default

	setattr(klass, "get", get)
	return klass


def validate_against(schema: ValidationSchema = None, inp=None, unknown=False, bulk: bool = False):
	if not isinstance(schema, ValidationSchema):
		raise ValidatorExceptions.InvalidValidationSchema

	if not ((bulk and isinstance(inp, list)) or (not bulk and isinstance(inp, dict))):
		raise ValidatorExceptions.InvalidValidationInput

	errors = {}
	schema, inp = __parse_schema_and_inp_for_bulk_validation(schema, inp, bulk=bulk)
	try:
		from cerberus.validator import Validator
		_validator = Validator(schema, allow_unknown=unknown)
		_validator.validate(inp)
		errors = _validator.errors
	except Exception as e:
		raise ValidatorExceptions.ValidationFailed
	return __formatted_validation_errors(errors, bulk=bulk)


def validate_request_data(payload_schema: ValidationSchema = None, param_schema: ValidationSchema = None, **opt):
	allow_unknown = opt.get("unknown") == True
	bulk_inp = opt.get("bulk_inp") == True

	def outer_func(_func):
		@wraps(_func)
		def inner_func(cls, request: drf_request.Request, *args, **kwargs):

			try:
				is_valid_payload_schema = isinstance(payload_schema, ValidationSchema)
				is_valid_param_schema = isinstance(param_schema, ValidationSchema)
				if (not is_valid_payload_schema and not is_valid_param_schema):
					raise ValidatorExceptions.InvalidValidationSchema

				# validate paload data if payload rules are defined
				if isinstance(payload_schema, ValidationSchema):
					_payload = __parse_payload_from_request(request=request)
					payload_validation_errors = validate_against(
						schema=payload_schema, inp=_payload, unknown=allow_unknown, bulk=bulk_inp
					)
					if payload_validation_errors:
						raise InvalidPayloadException(errors=payload_validation_errors)

				# validate parameter data like from URL/Query string if parameter
				# validation rules are defined
				if isinstance(param_schema, ValidationSchema):
					params_validation_errors = validate_against(schema=param_schema, inp=kwargs, unknown=True)
					if params_validation_errors:
						raise InvalidParamsException(errors=params_validation_errors)

				return _func(cls, *args, **dict(request=request, **kwargs))

			except InvalidPayloadException as e:
				return ApiResponse.exception(e)

			except InvalidParamsException as e:
				return ApiResponse.exception(e)

			except Exception as e:
				return ApiResponse.exception(e)

		return inner_func

	return outer_func


def validate_access(group: list = None, action: str = '', **opt):
	def decorator_function(_decorated_function):
		@wraps(_decorated_function)
		def wrapper_function(cls, request: drf_request.Request, *args, **kwargs):
			try:
				return _decorated_function(cls, *args, **dict(request=request, **kwargs))
			except Exception as e:
				ApiResponse.error(e)

		return wrapper_function

	return decorator_function
