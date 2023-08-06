{% macro current_timestamp() -%}
  {{ adapter.dispatch('current_timestamp', 'dbt')() }}
{%- endmacro %}

{% macro default__current_timestamp() -%}
  {{ exceptions.raise_not_implemented(
    'current_timestamp macro not implemented for adapter '+adapter.type()) }}
{%- endmacro %}