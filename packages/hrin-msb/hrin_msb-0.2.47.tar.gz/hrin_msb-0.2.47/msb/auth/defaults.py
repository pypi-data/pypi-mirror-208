from datetime import timedelta

from .constants import MSB_JWT_TOKEN_VALIDATOR, DefaultJwtConfig
from .users import TokenUser


def jwt_user_auth_rule(user: TokenUser):
	return user


class DefaultJwtAuthSettings:

	def __init__(self, signing_key: str, **opt):
		self.signing_key = signing_key
		self.verifying_key = opt.get('verifying_key') or signing_key
		self.token_user_class = opt.get('token_user_class') or DefaultJwtConfig.user_class
		self.user_id_claim = opt.get('user_id_claim') or DefaultJwtConfig.userid_claim
		self.user_authentication_rule = opt.get('user_authentication_rule') or DefaultJwtConfig.auth_rule
		self.algorithm = opt.get('algorithm') or DefaultJwtConfig.algorithm_hs256
		self.auth_header_types = opt.get('auth_header_types') or DefaultJwtConfig.auth_header_types
		self.auth_header_name = opt.get('auth_header_name') or DefaultJwtConfig.auth_header_name
		self.user_id_field = opt.get('user_id_field') or DefaultJwtConfig.userid_field
		self.token_type_claim = opt.get('token_type_claim') or DefaultJwtConfig.token_type_claim
		self.jti_claim = opt.get('jti_claim') or DefaultJwtConfig.jti_claim
		self.access_token_lifetime = opt.get('access_token_lifetime') or DefaultJwtConfig.access_token_lifetime
		self.refresh_token_lifetime = opt.get('refresh_token_lifetime') or DefaultJwtConfig.refresh_token_lifetime
		self.rotate_refresh_tokens = opt.get('rotate_refresh_tokens') or DefaultJwtConfig.rotate_refresh_tokens
		self.blacklist_after_rotation = opt.get(
			'blacklist_after_rotation') or DefaultJwtConfig.blacklist_after_rotation
		self.audience = opt.get('audience') or DefaultJwtConfig.audience
		self.issuer = opt.get('issuer') or DefaultJwtConfig.audience

	@property
	def authentication_classes(self):
		return [MSB_JWT_TOKEN_VALIDATOR]

	@property
	def for_token_validation(self) -> dict:
		return {
			'TOKEN_USER_CLASS': self.token_user_class,
			'USER_ID_CLAIM': self.user_id_claim,
			'USER_AUTHENTICATION_RULE': self.user_authentication_rule,
			'ALGORITHM': self.algorithm,
			'AUTH_HEADER_TYPES': self.auth_header_types,
			'AUTH_HEADER_NAME': self.auth_header_name,
			'USER_ID_FIELD': self.user_id_field,
			'TOKEN_TYPE_CLAIM': self.token_type_claim,
			'JTI_CLAIM': self.jti_claim,
			'SIGNING_KEY': self.signing_key,
			'VERIFYING_KEY': self.verifying_key,
		}

	@property
	def for_authentication(self) -> dict:
		return {
			**self.for_token_validation,
			'ROTATE_REFRESH_TOKENS': self.rotate_refresh_tokens,
			'BLACKLIST_AFTER_ROTATION': self.blacklist_after_rotation,
			'ACCESS_TOKEN_LIFETIME': timedelta(minutes=self.access_token_lifetime),
			'REFRESH_TOKEN_LIFETIME': timedelta(minutes=self.refresh_token_lifetime),
			'AUDIENCE': self.audience,
			'ISSUER': self.issuer,
		}
