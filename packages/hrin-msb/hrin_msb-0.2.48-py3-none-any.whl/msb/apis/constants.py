CRUD_URL_PK = '/<str:pk>'
CRUD_URL_PK_NAME = "pk"
MAX_FETCH_LIMIT = 100
DEFAULT_LOGGER_NAME = 'root'


class REQUEST_METHODS:
	POST = "post"
	PUT = "put"
	GET = "get"
	DELETE = "delete"

	ALL = [POST, PUT, GET, DELETE]


class CrudActions:
	create = 'create'
	retrieve = 'retrieve'
	list = 'list'
	search = 'search'

	update = 'update'
	bulk_update = 'bulk_update'

	delete = 'delete'
	bulk_delete = 'bulk_delete'

	all = [create, retrieve, update, delete, bulk_delete, bulk_update, list]
	single_read = [retrieve, ]
	create_only = [create]
	create_and_update = [create, update, bulk_update]
	full_read = [retrieve, list]
	full_write = [*create_and_update, delete, bulk_delete]


class CrudMethods:
	create = 'create'
	retrieve = 'retrieve'
	list = 'list'
	search = 'search'
	update = 'update'
	bulk_update = 'bulk_update'
	delete = 'delete'
	bulk_delete = 'bulk_delete'
	not_found = 'api_not_found'
