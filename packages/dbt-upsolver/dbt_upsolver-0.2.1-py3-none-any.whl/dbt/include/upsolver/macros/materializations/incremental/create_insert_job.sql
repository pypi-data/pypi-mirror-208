{% macro get_create_insert_job_sql(job_identifier, table, sync, options, map_columns_by_name) -%}

  {% set enriched_options = adapter.enrich_options(options, 'upsolver_data_lake', 'transformation_options') %}

  CREATE
  {% if sync %}
    SYNC
  {% endif %}
  JOB {{job_identifier}}
    {{ render_options(enriched_options, 'create') }}
  AS INSERT INTO {{table}}
  {% if map_columns_by_name %}
    MAP_COLUMNS_BY_NAME
  {% endif %}
  {{sql}}

{%- endmacro %}
