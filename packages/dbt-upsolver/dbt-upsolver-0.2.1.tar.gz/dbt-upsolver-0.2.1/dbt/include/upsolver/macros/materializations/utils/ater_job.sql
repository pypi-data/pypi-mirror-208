{% macro get_alter_job_sql(job_identifier, options, incremental_strategy, source) -%}

  {% if incremental_strategy %}
    {% set enriched_options = adapter.enrich_options(options, 'upsolver_data_lake', 'transformation_options') %}
  {% else  %}
    {% set enriched_options, _ = adapter.separate_options(options, source) %}
  {% endif %}
  {% set enriched_editable_options = adapter.filter_options(enriched_options, 'editable') %}

  ALTER JOB {{job_identifier}}
    {{ render_options(enriched_editable_options, 'alter') }}

{%- endmacro %}
