{% materialization incremental, adapter='upsolver' %}

  {%- set identifier = model['alias'] -%}
  {% set incremental_strategy = config.get('incremental_strategy', False) %}
  {% set partition_by = config.get('partition_by', []) %}
  {% set sync = config.get('sync', False) %}
  {% set options = config.get('options', {}) %}
  {% set source = config.get('source', none) %}
  {% set delete_condition = config.get('delete_condition', False) %}
  {% set partition_by = config.get('partition_by', []) %}
  {% set primary_key = config.get('primary_key', []) %}
  {% set map_columns_by_name = config.get('map_columns_by_name', False) %}
  {% set job_identifier = identifier + '_job' %}

  {%- set old_relation = adapter.get_relation(identifier=job_identifier,
                                              schema=schema,
                                              database=database) -%}
  {%- set target_relation = api.Relation.create(identifier=job_identifier,
                                                schema=schema,
                                                database=database,
                                                type='incremental') -%}

  {%- set table_relation = api.Relation.create(identifier=identifier,
                                                    schema=schema,
                                                    database=database,
                                                    type='table') -%}

  {{ run_hooks(pre_hooks, inside_transaction=False) }}
  {{ run_hooks(pre_hooks, inside_transaction=True) }}

  {%- call statement('create_table_if_not_exists') -%}
    {{ get_create_table_if_not_exists_sql(table_relation, partition_by, primary_key, options) }}
  {%- endcall -%}

  {% if old_relation %}
    {% call statement('main') -%}
      {{ get_alter_job_sql(job_identifier, options, incremental_strategy, source) }}
    {%- endcall %}
  {% else %}
    {% call statement('main') -%}
      {% if incremental_strategy == 'merge' %}
        {{ get_create_merge_job_sql(job_identifier, table_relation, sync,
                                    options, primary_key, delete_condition) }}
      {% elif incremental_strategy == 'insert' %}
        {{ get_create_insert_job_sql(job_identifier,
                                    table_relation, sync, options,
                                    map_columns_by_name) }}

      {% else  %}
        {{ get_create_copy_job_sql(job_identifier, sql,
                                   table_relation, sync, options, source) }}

      {% endif %}
    {%- endcall %}
  {%- endif %}

  {% do persist_docs(target_relation, model) %}
  {% do persist_docs(table_relation, model) %}

  {{ run_hooks(post_hooks, inside_transaction=False) }}
  {{ run_hooks(post_hooks, inside_transaction=True) }}

  {{ return({'relations': [target_relation, table_relation]}) }}
{% endmaterialization %}
