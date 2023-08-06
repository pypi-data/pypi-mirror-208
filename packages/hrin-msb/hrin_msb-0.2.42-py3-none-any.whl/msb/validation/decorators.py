from functools import wraps

from .utils import (validate_inp_payload, validate_inp_parameters, Request, ValidationSchema)


def validation_schema_wrapper(klass):
	def get(key: str, default=None) -> ValidationSchema | None:
		if hasattr(klass, key) and isinstance((schema := getattr(klass, key)), ValidationSchema):
			return schema
		return default

	setattr(klass, "get", get)
	return klass


def validate_input(payload_schema: ValidationSchema = None, param_schema: ValidationSchema = None, **opt):
	allow_unknown = opt.get("unknown") == True
	bulk_inp = opt.get("bulk_inp") == True

	def outer_func(_func):
		@wraps(_func)
		def inner_func(cls, request: Request, *args, **kwargs):

			"""
			validate paload data if payload rules are defined
			"""
			if isinstance(payload_schema, ValidationSchema):
				validate_inp_payload(payload_schema, request, allow_unknown, bulk_inp)

			"""
			 validate parameter data like from URL/Query string if parameter validation rules are defined
			"""
			if isinstance(param_schema, ValidationSchema):
				validate_inp_parameters(param_schema, kwargs, allow_unknown=True)

			return _func(cls, *args, **dict(request=request, **kwargs))

		return inner_func

	return outer_func


def validate_permission(*permissions, **opt):
	def decorator_function(_decorated_function):
		@wraps(_decorated_function)
		def wrapper_function(cls, request: Request, *args, **kwargs):
			cls.permission_classes = permissions
			return _decorated_function(cls, *args, **dict(request=request, **kwargs))

		return wrapper_function

	return decorator_function
