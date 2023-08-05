"""
HTTP HEADER NAMES
"""

HEADER_NAME_CONTENT_TYPE = "Content-Type"
HEADER_NAME_AUTHORIZATION = "Authorization"
AUTHORIZATION_NAME_BEARER_TOKEN = "Bearer"

"""
HTTP CONTENT TYPE NAMES
"""
CONTENT_TYPE_APPLICATION_JSON = "application/json"
AUTHORIZATION_BEARER_TOKEN_STRING = "Bearer {token}"


class HttpContentType:
	APPLICATION_JSON = "application/json"


class HttpHeaders:
	CONTENT_TYPE = "Content-Type"
	AUTHORIZATION = "Authorization"
	BEARER_TOKEN_VALUE = "Bearer {token}"


class RequestMethod:
	GET = "get"
	POST = "post"
	PUT = "put"
	DELETE = "delete"
