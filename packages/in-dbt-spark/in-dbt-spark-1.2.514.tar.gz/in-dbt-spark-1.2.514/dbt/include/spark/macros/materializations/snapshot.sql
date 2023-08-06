{% macro spark__snapshot_hash_arguments(args) -%}
    md5({%- for arg in args -%}
        coalesce(cast({{ arg }} as string ), '')
        {% if not loop.last %} || '|' || {% endif %}
    {%- endfor -%})
{%- endmacro %}


{% macro spark__snapshot_string_as_time(timestamp) -%}
    {%- set result = "to_timestamp('" ~ timestamp ~ "')" -%}
    {{ return(result) }}
{%- endmacro %}

{% macro build_merge_sql_hive(target, source, insert_cols) -%}

    select
        {% for column in insert_cols %}
          {% set column_name = column.name %}
          {{ ' case when t.' ~ column_name ~ ' is null then s.' ~ column_name ~ ' else t.' ~ column_name  ~ ' end as ' ~ column_name ~ ',' }}
        {% endfor %}
    case when t.dbt_scd_id is null then s.dbt_scd_id else t.dbt_scd_id end as dbt_scd_id,
    case when t.dbt_updated_at is null then s.dbt_updated_at else t.dbt_updated_at end as dbt_updated_at,
    case when t.dbt_valid_from is null then s.dbt_valid_from else t.dbt_valid_from end as dbt_valid_from,
    case when t.dbt_valid_to is null and s.dbt_change_type in ('update', 'delete') then s.dbt_valid_to else t.dbt_valid_to end as dbt_valid_to
    from {{ target }} t full outer join {{ source }} s on t.dbt_scd_id = s.dbt_scd_id;

{% endmacro %}

{% macro merge_sql_hive(target, source, insert_cols) -%}

    {% set tmp_identifier = target.identifier ~ '__dbt_merge' %}

    {%- set tmp_relation = api.Relation.create(identifier=tmp_identifier,
                                                  schema=target.schema,
                                                  database=none,
                                                  type='table') -%}
    {% set select = build_merge_sql_hive(target, source, insert_cols) %}

    {% call statement('build_snapshot_merge_relation') %}
        {{ log(" build_snapshot_merge_relation create_table_as description: ******* ") }}
        {% do adapter.drop_relation(tmp_relation) %}
        {{ create_table_as(False, tmp_relation, select) }}
    {% endcall %}

    {% do return(tmp_relation) %}
{% endmacro %}

{% macro insert_overwrite(target, source) -%}

   INSERT OVERWRITE TABLE {{ target }} select * from {{ source }};
{% endmacro %}



{% macro spark__snapshot_merge_sql(target, source, insert_cols) -%}

    merge into {{ target }} as DBT_INTERNAL_DEST
    {% if target.is_iceberg %}
      {# create view only supports a name (no catalog, or schema) #}
      using {{ source.identifier }} as DBT_INTERNAL_SOURCE
    {% else %}
      using {{ source }} as DBT_INTERNAL_SOURCE
    {% endif %}
    on DBT_INTERNAL_SOURCE.dbt_scd_id = DBT_INTERNAL_DEST.dbt_scd_id
    when matched
     and DBT_INTERNAL_DEST.dbt_valid_to is null
     and DBT_INTERNAL_SOURCE.dbt_change_type in ('update', 'delete')
        then update
        set dbt_valid_to = DBT_INTERNAL_SOURCE.dbt_valid_to

    when not matched
     and DBT_INTERNAL_SOURCE.dbt_change_type = 'insert'
        then insert *
    ;
{% endmacro %}


{% macro spark_build_snapshot_staging_table(strategy, sql, target_relation, file_format) %}
    {% set tmp_identifier = target_relation.identifier ~ '__dbt_tmp' %}

    {% if target_relation.is_iceberg %}
      {# iceberg catalog does not support create view, but regular spark does. We removed the catalog and schema #}
      {%- set tmp_relation = api.Relation.create(identifier=tmp_identifier,
                                                    schema=none,
                                                    database=none,
                                                    type='view') -%}
    {% elif target_relation.is_openhouse %}
      {# Views spanning multiple catalogs have undefined behavior currently #}
      {%- set tmp_relation = api.Relation.create(identifier=tmp_identifier,
                                                    schema=target_relation.schema,
                                                    database=target_relation.database,
                                                    type='table') -%}
    {% else %}
      {%- set tmp_relation = api.Relation.create(identifier=tmp_identifier,
                                                    schema=target_relation.schema,
                                                    database=none,
                                                    type='view') -%}
    {% endif %}

    {% set select = snapshot_staging_table(strategy, sql, target_relation) %}

    {# needs to be a non-temp view so that its columns can be ascertained via `describe` #}
    {% call statement('build_snapshot_staging_relation') %}
        {% if target_relation.is_openhouse %}
          {% do adapter.drop_relation(tmp_relation) %}
          {{ create_table_as(False, tmp_relation, select) }}
        {% else %}
          {{ create_view_as(tmp_relation, select) }}
        {% endif %}
    {% endcall %}

    {% do return(tmp_relation) %}
{% endmacro %}


{% macro spark__post_snapshot(staging_relation) %}
    {% do adapter.drop_relation(staging_relation) %}
{% endmacro %}


{% macro spark__create_columns(relation, columns) %}
    {% if columns|length > 0 %}
    {% call statement() %}
      alter table {{ relation }} add columns (
        {% for column in columns %}
          `{{ column.name }}` {{ column.data_type }} {{- ',' if not loop.last -}}
        {% endfor %}
      );
    {% endcall %}
    {% endif %}
{% endmacro %}


{% materialization snapshot, adapter='spark' %}
  {%- set config = model['config'] -%}

  {%- set target_table = model.get('alias', model.get('name')) -%}

  {%- set strategy_name = config.get('strategy') -%}
  {%- set unique_key = config.get('unique_key') %}
  {%- set file_format = config.get('file_format', 'openhouse') -%}

  {% set target_relation_exists, target_relation = get_or_create_relation(
          database=none,
          schema=model.schema,
          identifier=target_table,
          type='table') -%}

  {% if not adapter.check_schema_exists(model.database, model.schema) %}
    {% do exceptions.raise_compiler_error("Self-serve schema creation is not currently supported in OpenHouse. Please reach out in #ask_openhouse to manually provision your database.") %}
  {% endif %}

  {%- if not target_relation.is_table -%}
    {% do exceptions.relation_wrong_type(target_relation, 'table') %}
  {%- endif -%}

  {# -- TODO: DATAFND-1122 Hard coding the catalog as a workaround for APA-75325. Need to remove this once the spark v2 fix is deployed #}
  {% do adapter.dispatch('use_catalog', 'dbt')('spark_catalog') %}

  {{ run_hooks(pre_hooks, inside_transaction=False) }}

  {{ run_hooks(pre_hooks, inside_transaction=True) }}

  {% set strategy_macro = strategy_dispatch(strategy_name) %}
  {% set strategy = strategy_macro(model, "snapshotted_data", "source_data", config, target_relation_exists) %}

  {% if not target_relation_exists %}

      {% set build_sql = build_snapshot_table(strategy, model['compiled_sql']) %}
      {% set final_sql = create_table_as(False, target_relation, build_sql) %}

  {% else %}

      {{ adapter.valid_snapshot_target(target_relation) }}

      -- create temp delta table (table_name__dbt_tmp) with changetype as update/insert/delete
      {% set staging_table = spark_build_snapshot_staging_table(strategy, sql, target_relation, file_format) %}

      -- this may no-op if the database does not require column expansion
      {% do adapter.expand_target_column_types(from_relation=staging_table,
                                               to_relation=target_relation) %}

      {% set missing_columns = adapter.get_missing_columns(staging_table, target_relation)
                                   | rejectattr('name', 'equalto', 'dbt_change_type')
                                   | rejectattr('name', 'equalto', 'DBT_CHANGE_TYPE')
                                   | rejectattr('name', 'equalto', 'dbt_unique_key')
                                   | rejectattr('name', 'equalto', 'DBT_UNIQUE_KEY')
                                   | list %}

      {% do create_columns(target_relation, missing_columns) %}

      {% set staging_columns = adapter.get_columns_in_relation(staging_table)
                                   | rejectattr('name', 'equalto', 'dbt_change_type')
                                   | rejectattr('name', 'equalto', 'DBT_CHANGE_TYPE')
                                   | rejectattr('name', 'equalto', 'dbt_unique_key')
                                   | rejectattr('name', 'equalto', 'DBT_UNIQUE_KEY')
                                   | list %}

      -- only some file_formats support merge_into, others use full outer join to merge snapshot and source table
      -- TODO DATAFND-1019: use MERGE INTO for OpenHouse when `merge into` starts using column id ordering rather than ordinal
      {% if file_format in ['delta', 'iceberg', 'hudi'] %}
          {% set quoted_source_columns = [] %}
          {% for column in staging_columns %}
            {% do quoted_source_columns.append(adapter.quote(column.name)) %}
          {% endfor %}

          {% set final_sql = snapshot_merge_sql(
              target = target_relation,
              source = staging_table,
              insert_cols = quoted_source_columns)
          %}
      {% else %}
           {% set source_columns_updated = staging_columns
                                   | rejectattr('name', 'equalto', 'dbt_updated_at')
                                   | rejectattr('name', 'equalto', 'dbt_valid_from')
                                   | rejectattr('name', 'equalto', 'dbt_valid_to')
                                   | rejectattr('name', 'equalto', 'dbt_scd_id')
                                   | list %}

            -- merge old snapshot and table (table_name__dbt_tmp) to create  another temp table (table_name__dbt_merge)
           {% set merge_table = merge_sql_hive(
                target = target_relation,
                source = staging_table,
                insert_cols = source_columns_updated)
           %}
            -- overwrite snapshot table with merge table creates above (table_name__dbt_merge)
           {% set final_sql = insert_overwrite(
            target = target_relation,
            source = merge_table)
           %}
      {% endif %}
  {% endif %}

  {% call statement('main') %}
      {{ final_sql }}
  {% endcall %}

  {% set should_revoke = should_revoke(target_relation_exists, full_refresh_mode) %}
  {% do apply_grants(target_relation, grant_config, should_revoke) %}

  {% do persist_docs(target_relation, model) %}

  {{ run_hooks(post_hooks, inside_transaction=True) }}

  {{ adapter.commit() }}

  {% if staging_table is defined %}
      {% do post_snapshot(staging_table) %}
  {% endif %}
  {% if merge_table is defined %}
      {% do post_snapshot(merge_table) %}
  {% endif %}

  {{ run_hooks(post_hooks, inside_transaction=False) }}

  {{ return({'relations': [target_relation]}) }}

{% endmaterialization %}
