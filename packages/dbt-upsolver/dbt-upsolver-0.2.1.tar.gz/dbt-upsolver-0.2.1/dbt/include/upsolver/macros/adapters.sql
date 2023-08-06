{% macro upsolver__alter_column_type(relation,column_name,new_column_type) -%}
'''Changes column name or data type'''
/*
    1. Create a new column (w/ temp name and correct type)
    2. Copy data over to it
    3. Drop the existing column (cascade!)
    4. Rename the new column to existing column
*/
{% endmacro %}

{macro upsolver__check_schema_exists(information_schema,schema) -%}
'''Checks if schema name exists and returns number or times it shows up.'''
  {{ print('Checks if schema name exists') }}
{% endmacro %}

{% macro upsolver__drop_relation(relation) -%}
'''Deletes relatonship identifer between tables.'''
  {% call statement('drop_relation') -%}
    drop materialized view {{ relation }}
  {%- endcall %}
{% endmacro %}

{% macro upsolver__drop_schema(relation) -%}
'''drops a schema in a target database.'''
/*
  1. If database exists
  2. search all calls of schema, and change include value to False, cascade it to backtrack
*/
{% endmacro %}

{% macro upsolver__get_columns_in_relation(relation) -%}
'''Returns a list of Columns in a table.'''
/*
  1. select as many values from column as needed
  2. search relations to columns
  3. where table name is equal to the relation identifier
  4. if a relation schema exists and table schema is equal to the relation schema
  5. order in whatever way you want to call.
  6. create a table by loading result from call
  7. return new table
*/
{% endmacro %}

{% macro list_relation_without_caching(schema_relation, relation_type) -%}
  {% set source = relation_type +'s' %}
  {% call statement('list_relation_without_caching', fetch_result=True) -%}
    select
      '{{ schema_relation.database }}' as database,
      name,
      '{{ schema_relation.schema }}' as schema,
      {% if relation_type == 'job' %}
        'incremental' as type
      {% else %}
        '{{ relation_type }}' as type
      {% endif %}
    from system.information_schema."{{ source }}"
      {% if relation_type in ['table', 'view'] %}
        where schema = '{{ schema_relation.schema }}'
      {% endif %}
  {% endcall %}
  {{ return(load_result('list_relation_without_caching').table) }}
{% endmacro %}

{% macro upsolver__list_schemas(database) -%}
'''Returns a table of unique schemas.'''
/*
  1. search schemea by specific name
  2. create a table with names
*/
{% endmacro %}

{% macro upsolver__rename_relation(from_relation, to_relation) -%}
'''Renames a relation in the database.'''
/*
  1. Search for a specific relation name
  2. alter table by targeting specific name and passing in new name
*/
{% endmacro %}

{% macro upsolver__truncate_relation(relation) -%}
'''Removes all rows from a targeted set of tables.'''
/*
  1. grab all tables tied to the relation
  2. remove rows from relations
*/
{% endmacro %}

{% macro upsolver__current_timestamp() -%}
'''Returns current UTC time'''
{# docs show not to be implemented currently. #}
{% endmacro %}

{% macro upsolver__create_arbitrary_object(sql) -%}
    {{ sql }}
{%- endmacro %}
