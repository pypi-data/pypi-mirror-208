from .decorators import (
	validation_schema_wrapper, require_inputs,
	validate_inp_parameters, validate_inp_payload
)
from .exceptions import *
from .rules import (DefaultRules)
from .schema import (RuleSchema, InputField, ValidationSchema)
from .utils import validate_against


class Validate:
	request_data = require_inputs
	params = validate_inp_parameters
	payload = validate_inp_payload


__all__ = [
	"require_permissions", "require_inputs", "validate_inp_parameters", "validate_inp_payload", "validate_against",
	"validation_schema_wrapper", "RuleSchema", "InputField", "ValidationSchema", "DefaultRules",
]
