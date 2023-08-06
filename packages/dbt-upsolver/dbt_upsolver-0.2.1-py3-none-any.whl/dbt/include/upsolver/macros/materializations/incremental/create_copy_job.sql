{% macro get_create_copy_job_sql(job_identifier, sql, table, sync, options, source) -%}

    {% set connection_identifier = adapter.get_connection_from_sql(sql) %}
    {% set job_options, source_options = adapter.separate_options(options, source) %}

    CREATE
    {% if sync %}
      SYNC
    {% endif %}
    JOB {{job_identifier}}
    {{ render_options(job_options, 'create') }}
    AS COPY FROM {{source}} {{connection_identifier}}
    {{ render_options(source_options, 'create') }}
    INTO {{table}}

{%- endmacro %}
