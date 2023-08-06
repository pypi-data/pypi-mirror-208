Connection_options = {
  "s3": {
        "aws_role": {"type": "text", "editable": True, "optional": True},
        "external_id": {"type": "text", "editable": True, "optional": True},
        "aws_access_key_id": {"type": "text", "editable": True, "optional": True},
        "aws_secret_access_key_id": {"type": "text", "editable": True, "optional": True},
        "path_display_filter": {"type": "text", "editable": True, "optional": True},
        "path_display_filters": {"type": "list", "editable": True, "optional": True},
        "read_only": {"type": "boolean", "editable": True, "optional": True},
        "encryption_kms_key": {"type": "text", "editable": True, "optional": True},
        "encryption_customer_kms_key": {"type": "text", "editable": True, "optional": True},
        "comment": {"type": "text", "editable": True, "optional": True}
  },
    "kafka": {
        "host": {"type": "text", "editable": False, "optional": False},
        "hosts": {"type": "list", "editable": False, "optional": False},
        "consumer_properties": {"type": "text", "editable": True, "optional": True},
        "version": {"type": "value", "editable": False, "optional": True},
        "require_static_ip": {"type": "boolean", "editable": True, "optional": True},
        "ssl": {"type": "boolean", "editable": True, "optional": True},
        "topic_display_filter": {"type": "text", "editable": True, "optional": True},
        "comment": {"type": "text", "editable": True, "optional": True}
    },
    "glue_catalog": {
        "aws_role": {"type": "text", "editable": True, "optional": True},
        "external_id": {"type": "text", "editable": True, "optional": True},
        "aws_access_key_id": {"type": "text", "editable": True, "optional": True},
        "aws_secret_access_key": {"type": "text", "editable": True, "optional": True},
        "default_storage_connection": {"type": "identifier", "editable": False, "optional": False},
        "default_storage_location": {"type": "text", "editable": False, "optional": False},
        "region": {"type": "text", "editable": False, "optional": True},
        "database_display_filter": {"type": "text", "editable": True, "optional": True},
        "database_display_filters": {"type": "list", "editable": True, "optional": True},
        "comment": {"type": "text", "editable": True, "optional": True}
    },
    "kinesis": {
        "aws_role": {"type": "text", "editable": True, "optional": True},
        "external_id": {"type": "text", "editable": True, "optional": True},
        "aws_access_key_id": {"type": "text", "editable": True, "optional": True},
        "aws_secret_access_key": {"type": "text", "editable": True, "optional": True},
        "region": {"type": "text", "editable": False, "optional": False},
        "read_only": {"type": "boolean", "editable": False, "optional": True},
        "max_writers": {"type": "integer", "editable": True, "optional": True},
        "stream_display_filter": {"type": "text", "editable": True, "optional": True},
        "stream_display_filters": {"type": "list", "editable": True, "optional": True},
        "comment": {"type": "text", "editable": True, "optional": True}
    },
    "snowflake": {
        "connection_string": {"type": "text", "editable": True, "optional": False},
        "user_name": {"type": "text", "editable": True, "optional": False},
        "password": {"type": "text", "editable": True, "optional": False},
        "max_concurrent_connections": {"type": "integer", "editable": True, "optional": True},
        "comment": {"type": "text", "editable": True, "optional": True}
    },
    "redshift": {
        "connection_string": {"type": "text", "editable": True, "optional": False},
        "user_name": {"type": "text", "editable": True, "optional": False},
        "password": {"type": "text", "editable": True, "optional": False},
        "max_concurrent_connections": {"type": "integer", "editable": True, "optional": True},
        "comment": {"type": "text", "editable": True, "optional": True}
    },
    "mysql": {
        "connection_string": {"type": "text", "editable": True, "optional": False},
        "user_name": {"type": "text", "editable": True, "optional": False},
        "password": {"type": "text", "editable": True, "optional": False},
        "max_concurrent_connections": {"type": "integer", "editable": True, "optional": True},
        "comment": {"type": "text", "editable": True, "optional": True}
    },
    "postgres": {
        "connection_string": {"type": "text", "editable": True, "optional": False},
        "user_name": {"type": "text", "editable": True, "optional": False},
        "password": {"type": "text", "editable": True, "optional": False},
        "comment": {"type": "text", "editable": True, "optional": True}
    },
    "elasticsearch": {
        "connection_string": {"type": "text", "editable": True, "optional": False},
        "user_name": {"type": "text", "editable": True, "optional": False},
        "password": {"type": "text", "editable": True, "optional": False}
    }
}
