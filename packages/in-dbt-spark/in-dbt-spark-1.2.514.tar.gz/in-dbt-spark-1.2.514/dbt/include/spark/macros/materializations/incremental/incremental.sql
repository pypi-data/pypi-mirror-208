{% materialization incremental, adapter='spark' -%}

  {#-- Validate early so we don't run SQL if the file_format + strategy combo is invalid --#}
  {%- set raw_file_format = config.get('file_format', default='openhouse') -%}
  {%- set raw_strategy = config.get('incremental_strategy', default='append') -%}
  {%- set grant_config = config.get('grants') -%}
  {%- set raw_retention = config.get('retention_period', none) -%}

  {%- set file_format = dbt_spark_validate_get_file_format(raw_file_format) -%}
  {%- set file_format = dbt_spark_validate_openhouse_configs(file_format) -%}
  {%- set strategy = dbt_spark_validate_get_incremental_strategy(raw_strategy, file_format) -%}
  {%- set retention = dbt_spark_validate_retention_configs(raw_retention,file_format) -%}

  {%- set catalog -%}
    {%- if not file_format == 'openhouse' -%}
      spark_catalog
    {%- else %}
      openhouse
    {%- endif -%}
  {%- endset -%}

  {%- set unique_key = config.get('unique_key', none) -%}
  {%- set raw_partition_by = config.get('partition_by', none) -%}

  {%- set full_refresh_mode = (should_full_refresh()) -%}

  {% set on_schema_change = incremental_validate_on_schema_change(config.get('on_schema_change'), default='ignore') %}

  {% set target_relation = this %}
  {% set existing_relation = load_relation(this) %}
  {% set tmp_relation = make_temp_relation(this) %}

  {% if strategy == 'insert_overwrite' and raw_partition_by %}
    {% call statement() %}
      set spark.sql.sources.partitionOverwriteMode = DYNAMIC
    {% endcall %}
  {% endif %}

  {# -- TODO: DATAFND-1122 Hard coding the catalog as a workaround for APA-75325. Need to remove this once the spark v2 fix is deployed #}
  {% do adapter.dispatch('use_catalog', 'dbt')('spark_catalog') %}

  {{ run_hooks(pre_hooks) }}

  {% set is_delta = (file_format == 'delta' and existing_relation.is_delta) %}

  {% if existing_relation is none %}
    {% set build_sql = create_table_as(False, target_relation, sql) %}
  {% elif existing_relation.is_view or full_refresh_mode %}
    {% if not is_delta %} {#-- If Delta, we will `create or replace` below, so no need to drop --#}
      {% do adapter.drop_relation(existing_relation) %}
    {% endif %}
    {% set build_sql = create_table_as(False, target_relation, sql) %}
  {% else %}
    {% do run_query(create_table_as(True, tmp_relation, sql)) %}
    {% do process_schema_changes(on_schema_change, tmp_relation, existing_relation) %}
    {% set build_sql = dbt_spark_get_incremental_sql(strategy, tmp_relation, target_relation, existing_relation, unique_key) %}
  {% endif %}

  {%- call statement('main') -%}
    {{ build_sql }}
  {%- endcall -%}

  {% set should_revoke = should_revoke(existing_relation, full_refresh_mode) %}
  {% do apply_grants(target_relation, grant_config, should_revoke) %}
  {% do apply_retention(target_relation, retention) %}
  {% do persist_docs(target_relation, model) %}

  {{ run_hooks(post_hooks) }}

  {{ return({'relations': [target_relation]}) }}

{%- endmaterialization %}
