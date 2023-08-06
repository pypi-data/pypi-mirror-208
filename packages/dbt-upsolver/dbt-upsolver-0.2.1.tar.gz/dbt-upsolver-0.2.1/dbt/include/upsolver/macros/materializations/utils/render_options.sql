{% macro render_options(options, statement) -%}

    {%- if  statement == 'alter' -%}
      {% set key = 'SET' %}
    {%- endif -%}
    {%- for k, v in options.items() -%}
      {% set value =  v['value'] %}
      {% if v['type'] == 'text' %}
        {{key}} {{k}} = '{{ value }}'
      {% elif v['type'] == 'identifier' %}
        {{key}} {{k}} = "{{ value }}"
      {% else %}
        {{key}} {{k}} = {{ value }}
      {%- endif -%}
    {%- endfor %}

{%- endmacro %}
