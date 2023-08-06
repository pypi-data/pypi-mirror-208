{% macro apply_retention(target_relation, retention) %}
  {{ return(adapter.dispatch('apply_retention', 'dbt')(target_relation, retention)) }}
{%- endmacro -%}

{% macro spark__apply_retention(relation, retention) %}
  {%- set file_format = config.get('file_format', 'openhouse') -%}
  {%- set raw_partition_by = config.get('partition_by', none) -%}
  {%- set partition_by_list = adapter.parse_partition_by(raw_partition_by) -%}
  {%- set ns = namespace(granularity=none) -%}

  {% if file_format == 'openhouse' %}
    {% if partition_by_list is not none %}
        {%- for partition_by in partition_by_list if partition_by.data_type.lower() == 'timestamp' -%}
            {% set ns.granularity = partition_by.granularity %}
        {%- endfor -%}
        {% set retention_query %}
        {% if retention is not none %}
            alter table {{ relation }} set policy (RETENTION={{ retention }})
        {% else %}
            {% if ns.granularity == 'hours' %}
                alter table {{ relation }} set policy (RETENTION=8760h)
            {% elif ns.granularity == 'days' %}
                alter table {{ relation }} set policy (RETENTION=365d)
            {% elif ns.granularity == 'months' %}
                alter table {{ relation }} set policy (RETENTION=12m)
            {% else %}
                alter table {{ relation }} set policy (RETENTION=1y)
            {% endif %}
        {% endif %}
        {% endset %}
        {% do run_query(retention_query) %}
    {% endif %}
  {% endif %}
{%- endmacro -%}
