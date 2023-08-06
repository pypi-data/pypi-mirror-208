Copy_options = {
  "kafka": {
    "source_options": {
        "topic_name": {"type": "text", "editable": False, "optional": False},
        "topic": {"type": "text", "editable": False, "optional": False}},
    "job_options": {
        "consumer_properties": {"type": "text", "editable": True, "optional": True},
        "reader_shards": {"type": "integer", "editable": True, "optional": True},
        "store_raw_data": {"type": "value", "editable": False, "optional": True},
        "start_from": {"type": "value", "editable": False, "optional": True},
        "end_at": {"type": "value", "editable": True, "optional": True},
        "compute_cluster": {"type": "identifier", "editable": True, "optional": True},
        "run_parallelism": {"type": "integer", "editable": True, "optional": True},
        "content_type": {"type": "value", "editable": True, "optional": True},
        "compression": {"type": "value", "editable": False, "optional": True},
        "comment": {"type": "text", "editable": True, "optional": True}
    }
  },
  "mysql": {
    "source_options": {
        "table_include_list": {"type": "list", "editable": True, "optional": True},
        "column_exclude_list": {"type": "list", "editable": True, "optional": True}
    },
    "job_options": {
        "skip_snapshots": {"type": "boolean", "editable": True, "optional": True},
        "end_at": {"type": "value", "editable": True, "optional": True},
        "compute_cluster": {"type": "identifier", "editable": True, "optional": True},
        "comment": {"type": "text", "editable": True, "optional": True}
    }
  },
  "postgres": {
    "source_options": {
        "table_include_list": {"type": "list", "editable": False, "optional": False},
        "column_exclude_list": {"type": "list", "editable": False, "optional": True}
    },
    "job_options": {
        "heartbeat_table": {"type": "text", "editable": False, "optional": True},
        "skip_snapshots": {"type": "boolean", "editable": False, "optional": True},
        "publication_name": {"type": "text", "editable": False, "optional": False},
        "end_at": {"type": "value", "editable": True, "optional": True},
        "compute_cluster": {"type": "identifier", "editable": True, "optional": True},
        "comment": {"type": "text", "editable": True, "optional": True},
        "parse_json_columns": {"type": "boolean", "editable": False, "optional": False}
    }
  },
  "s3": {
    "source_options": {
        "location": {"type": "text", "editable": False, "optional": False}
    },
    "job_options": {
        "file_pattern": {"type": "text", "editable": False, "optional": True},
        "delete_files_after_load": {"type": "boolean", "editable": False, "optional": True},
        "end_at": {"type": "value", "editable": True, "optional": True},
        "compute_cluster": {"type": "identifier", "editable": True, "optional": True},
        "run_parallelism": {"type": "integer", "editable": True, "optional": True},
        "content_type": {"type": "value", "editable": True, "optional": True},
        "compression": {"type": "value", "editable": False, "optional": True},
        "comment": {"type": "text", "editable": True, "optional": True}
    }
  },
    "kinesis": {
      "source_options": {
          "stream": {"type": "text", "editable": False, "optional": False}
      },
      "job_options": {
          "reader_shards": {"type": "integer", "editable": True, "optional": True},
          "store_raw_data": {"type": "boolean", "editable": False, "optional": True},
          "start_from": {"type": "value", "editable": False, "optional": True},
          "end_at": {"type": "value", "editable": False, "optional": True},
          "compute_cluster": {"type": "identifier", "editable": True, "optional": True},
          "run_parallelism": {"type": "integer", "editable": False, "optional": True},
          "content_type": {"type": "value", "editable": True, "optional": True},
          "compression": {"type": "value", "editable": False, "optional": True},
          "comment": {"type": "text", "editable": True, "optional": True}
      }
    }
}
