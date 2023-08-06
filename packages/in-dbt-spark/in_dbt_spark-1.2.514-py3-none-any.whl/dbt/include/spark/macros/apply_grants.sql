{% macro spark__copy_grants() %}

    {% if config.materialized == 'view' %}
        {#-- Spark views don't copy grants when they're replaced --#}
        {{ return(False) }}

    {% else %}
      {#-- This depends on how we're replacing the table, which depends on its file format
        -- Just play it safe by assuming that grants have been copied over, and need to be checked / possibly revoked
        -- We can make this more efficient in the future
      #}
        {{ return(True) }}

    {% endif %}
{% endmacro %}

{%- macro spark__get_grant_sql(relation, privilege, grantees) -%}
    {% if config.get('file_format', default='openhouse') == 'openhouse' %}
        grant {{ privilege }} on table {{ relation }} to {{ grantees[0] }}
    {%- else -%}
        grant {{ privilege }} on {{ relation }} to {{ adapter.quote(grantees[0]) }}
    {%- endif %}
{%- endmacro %}

{%- macro spark__get_revoke_sql(relation, privilege, grantees) -%}
    {% if config.get('file_format', default='openhouse') == 'openhouse' %}
        revoke {{ privilege }} on table {{ relation }} from {{ grantees[0] }}
    {%- else -%}
        revoke {{ privilege }} on {{ relation }} from {{ adapter.quote(grantees[0]) }}
    {%- endif %}
{%- endmacro %}


{%- macro spark__support_multiple_grantees_per_dcl_statement() -%}
    {{ return(False) }}
{%- endmacro -%}


{% macro spark__call_dcl_statements(dcl_statement_list) %}
    {% for dcl_statement in dcl_statement_list %}
        {% call statement('grant_or_revoke') %}
            {{ dcl_statement }}
        {% endcall %}
    {% endfor %}
{% endmacro %}

{% macro set_sharing_enabled(relation, sharing_enabled=True) %}
    {% call statement('sharing_enabled_policy') %}
        alter table {{ relation }} set policy (sharing={{ sharing_enabled }})
    {% endcall %}
{% endmacro %}

{% macro spark__apply_grants(relation, grant_config, should_revoke=True) %}
    {%- set file_format = config.get('file_format', default='openhouse') -%}
    {#-- Automatically enable sharing for OpenHouse outputs to allow GRANTS both within and outside of dbt --#}
    {% if file_format == 'openhouse' %}
        {{ set_sharing_enabled(relation, True) }}
    {% endif %}
    {#-- If grant_config is {} or None, this is a no-op --#}
    {% if grant_config %}
        {#-- OpenHouse file_formats support append-only granting behavior, ie., no automated revoking through dbt--#}
        {% if should_revoke and file_format != 'openhouse' %}
            {#-- We think previous grants may have carried over --#}
            {#-- Show current grants and calculate diffs --#}
            {% set current_grants_table = run_query(get_show_grant_sql(relation)) %}
            {% set current_grants_dict = adapter.standardize_grants_dict(current_grants_table) %}
            {% set needs_granting = diff_of_two_dicts(grant_config, current_grants_dict) %}
            {% set needs_revoking = diff_of_two_dicts(current_grants_dict, grant_config) %}
            {% if not (needs_granting or needs_revoking) %}
                {{ log('On ' ~ relation ~': All grants are in place, no revocation or granting needed.')}}
            {% endif %}
        {% else %}
            {#-- We don't think there's any chance of previous grants having carried over. --#}
            {#-- Jump straight to granting what the user has configured. --#}
            {% set needs_revoking = {} %}
            {% set needs_granting = grant_config %}
        {% endif %}
        {% if needs_granting or needs_revoking %}
            {% set revoke_statement_list = get_dcl_statement_list(relation, needs_revoking, get_revoke_sql) %}
            {% set grant_statement_list = get_dcl_statement_list(relation, needs_granting, get_grant_sql) %}
            {% set dcl_statement_list = revoke_statement_list + grant_statement_list %}
            {% if dcl_statement_list %}
                {{ call_dcl_statements(dcl_statement_list) }}
            {% endif %}
        {% endif %}
    {% endif %}
{% endmacro %}
