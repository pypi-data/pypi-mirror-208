from .dataclasses import (DbVendorConfig)

DJANGO_MIGRATION_DB_VENDOR_CONFIG: dict[str, DbVendorConfig] = dict(
	sqlite=DbVendorConfig(
		query_to_list_tables="SELECT tbl_name FROM sqlite_master WHERE type='table'",
		excluded_tables=["sqlite_master", "sqlite_sequence"],
		query_to_drop_table="DROP TABLE IF EXISTS {table_name};",

	),

	postgresql=DbVendorConfig(
		query_to_list_tables="select table_name from information_schema.tables WHERE table_schema in ('public')",
		excluded_tables=[],
		query_to_drop_table="DROP TABLE IF EXISTS {table_name} CASCADE;",
	)

)

REGEX_TO_SELECT_ENV_VARIABLE = r"(\s)*?([\w_]*)=(['\"])?([\w\d()\-:/*?=@.+!%$_#^&,]*)(['\"])?([\s\r\n]*)"
REGEX_TO_REPLACE_ENV_VARIABLE = r'\1\2=\3\2_VALUE\5\6'
