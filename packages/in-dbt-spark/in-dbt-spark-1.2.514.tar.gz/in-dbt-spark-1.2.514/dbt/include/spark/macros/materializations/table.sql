{% materialization table, adapter = 'spark' %}

  {%- set identifier = model['alias'] -%}
  {%- set grant_config = config.get('grants') -%}
  {%- set raw_retention = config.get('retention_period', none) -%}

  {%- set raw_file_format = config.get('file_format', default='openhouse') -%}
  {%- set file_format = dbt_spark_validate_openhouse_configs(raw_file_format) -%}
  {%- set retention = dbt_spark_validate_retention_configs(raw_retention,file_format) -%}

  {%- set catalog -%}
    {%- if not file_format == 'openhouse' -%}
      spark_catalog
    {%- else %}
      openhouse
    {%- endif -%}
  {%- endset -%}

  {%- set old_relation = adapter.get_relation(database=database, schema=schema, identifier=identifier) -%}
  {%- set target_relation = api.Relation.create(identifier=identifier,
                                                schema=schema,
                                                database=database,
                                                type='table') -%}

  {# -- TODO: DATAFND-1122 Hard coding the catalog as a workaround for APA-75325. Need to remove this once the spark v2 fix is deployed #}
  {% do adapter.dispatch('use_catalog', 'dbt')('spark_catalog') %}

  {{ run_hooks(pre_hooks) }}

  -- setup: if the target relation already exists, drop it
  -- in case if the existing and future table is delta, we want to do a
  -- create or replace table instead of dropping, so we don't have the table unavailable
  {% if old_relation and not (old_relation.is_delta and file_format == 'delta') -%}
    {{ adapter.drop_relation(old_relation) }}
  {%- endif %}

  {% if old_relation and not (old_relation.is_iceberg and file_format == 'iceberg') -%}
    {{ adapter.drop_relation(old_relation) }}
  {%- endif %}

  -- build model
  {% call statement('main') -%}
    {{ create_table_as(False, target_relation, sql) }}
  {%- endcall %}

  {% set should_revoke = should_revoke(old_relation, full_refresh_mode=True) %}
  {% do apply_grants(target_relation, grant_config, should_revoke) %}
  {% do apply_retention(target_relation, retention) %}
  {% do persist_docs(target_relation, model) %}

  {{ run_hooks(post_hooks) }}

  {{ return({'relations': [target_relation]})}}

{% endmaterialization %}
