Transformation_options = {
  "s3": {
        "run_interval": {"type": "ineger", "editable": False, "optional": True},
        "start_from": {"type": "value", "editable": False, "optional": True},
        "end_at": {"type": "value", "editable": True, "optional": True},
        "compute_cluster": {"type": "identifier", "editable": True, "optional": True},
        "allow_cartesian_products": {"type": "boolean", "editable": False, "optional": True},
        "aggregation_parallelism": {"type": "integer", "editable": True, "optional": True},
        "run_parallelism": {"type": "integer", "editable": True, "optional": True},
        "file_type": {"type": "value", "editable": False, "optional": False},
        "compression": {"type": "value", "editable": False, "optional": True},
        "date_pattern": {"type": "text", "editable": False, "optional": True},
        "output_offset": {"type": "integer", "editable": False, "optional": True},
        "location": {"type": "text", "editable": False, "optional": True}
  },
  'elasticsearch': {
        "run_interval": {"type": "ineger", "editable": False, "optional": True},
        "start_from": {"type": "value", "editable": False, "optional": True},
        "end_at": {"type": "value", "editable": True, "optional": True},
        "compute_cluster": {"type": "identifier", "editable": True, "optional": True},
        "allow_cartesian_products": {"type": "boolean", "editable": False, "optional": True},
        "aggregation_parallelism": {"type": "integer", "editable": True, "optional": True},
        "run_parallelism": {"type": "integer", "editable": True, "optional": True},
        "bulk_max_size_bytes": {"type": "integer", "editable": True, "optional": True},
        "index_partition_size": {"type": "value", "editable": True, "optional": True},
        "comment": {"type": "text", "editable": True, "optional": True}
  },
  'snowflake': {
        "run_interval": {"type": "ineger", "editable": False, "optional": True},
        "start_from": {"type": "value", "editable": False, "optional": True},
        "end_at": {"type": "value", "editable": True, "optional": True},
        "compute_cluster": {"type": "identifier", "editable": True, "optional": True},
        "allow_cartesian_products": {"type": "boolean", "editable": False, "optional": True},
        "aggregation_parallelism": {"type": "integer", "editable": True, "optional": True},
        "run_parallelism": {"type": "integer", "editable": True, "optional": True},
        "comment": {"type": "text", "editable": True, "optional": True}
  },
    'upsolver_data_lake': {
        "add_missing_columns": {"type": "boolean", "editable": False, "optional": True},
        "run_interval": {"type": "ineger", "editable": False, "optional": True},
        "start_from": {"type": "value", "editable": False, "optional": True},
        "end_at": {"type": "value", "editable": True, "optional": True},
        "compute_cluster": {"type": "identifier", "editable": True, "optional": True},
        "allow_cartesian_products": {"type": "boolean", "editable": False, "optional": True},
        "aggregation_parallelism": {"type": "integer", "editable": True, "optional": True},
        "run_parallelism": {"type": "integer", "editable": True, "optional": True},
        "comment": {"type": "text", "editable": True, "optional": True}
    },
    'redshift': {
        "run_interval": {"type": "ineger", "editable": False, "optional": True},
        "start_from": {"type": "value", "editable": False, "optional": True},
        "end_at": {"type": "value", "editable": True, "optional": True},
        "compute_cluster": {"type": "identifier", "editable": True, "optional": True},
        "allow_cartesian_products": {"type": "boolean", "editable": False, "optional": True},
        "aggregation_parallelism": {"type": "integer", "editable": True, "optional": True},
        "run_parallelism": {"type": "integer", "editable": True, "optional": True},
        "skip_faild_files": {"type": "boolean", "editable": False, "optional": True},
        "fail_on_write_error": {"type": "boolean", "editable": False, "optional": True},
        "comment": {"type": "text", "editable": True, "optional": True}
    }
}
