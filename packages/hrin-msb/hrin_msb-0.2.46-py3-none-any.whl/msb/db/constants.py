# Choices
CHOICE_STATUS = (
	('0', 'Inactive'),
	('1', 'Active')
)

# default column names

COLUMN_NAME_ACTIVE = 'active'
COLUMN_NAME_DELETED = 'is_deleted'

COLUMN_NAME_DELETED_BY = 'deleted_by'
COLUMN_NAME_DELETED_AT = 'deleted_at'

COLUMN_NAME_CREATED_BY = 'created_by'
COLUMN_NAME_CREATED_AT = 'created_at'

COLUMN_NAME_UPDATED_BY = 'updated_by'
COLUMN_NAME_UPDATED_AT = 'updated_at'

DEFAULT_APP_LABLES_TO_ROUTE: set = set()
DEFAULT_DATABASE_NAME: str = 'default'
DEFAULT_MIGRATION_DATABASE: list = [DEFAULT_DATABASE_NAME]

DB_ROUTER_OP_LIST = ('write', 'read', 'relation', 'migration')

DEFAULT_QUERY_OFFSET = 0
DEFAULT_QUERY_LIMIT = 500
