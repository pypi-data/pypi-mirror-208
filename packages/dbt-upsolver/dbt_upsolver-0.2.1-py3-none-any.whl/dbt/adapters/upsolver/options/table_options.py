Table_options = {
    "globally_unique_keys": {"type": "boolean", "editable": False, "optional": True},
    "storage_connection": {"type": "identifier", "editable": False, "optional": True},
    "storage_location": {"type": "text", "editable": False, "optional": True},
    "compute_cluster": {"type": "identifier", "editable": True, "optional": True},
    "compression": {"type": "value", "editable": True, "optional": True},
    "compaction_processes": {"type": "integer", "editable": True, "optional": True},
    "disable_compaction": {"type": "boolean", "editable": True, "optional": True},
    "retention_date_partition": {"type": "text", "editable": True, "optional": True},
    "table_data_retention": {"type": "text", "editable": True, "optional": True},
    "column_data_retention": {"type": "text", "editable": True, "optional": True},
    "comment": {"type": "text", "editable": True, "optional": True}
}
