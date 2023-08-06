Materialized_view_options = {
    "storage_connection": {"type": "identifier", "editable": False, "optional": True},
    "storage_location": {"type": "text", "editable": False, "optional": True},
    "max_time_travel_duration": {"type": "integer", "editable": True, "optional": True},
    "compute_cluster": {"type": "identifier", "editable": True, "optional": True},
}
