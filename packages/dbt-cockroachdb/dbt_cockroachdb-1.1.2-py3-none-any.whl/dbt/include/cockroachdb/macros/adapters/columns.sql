{% macro get_columns_in_relation(relation) -%}
  {{ return(adapter.dispatch('get_columns_in_relation', 'dbt')(relation)) }}
{% endmacro %}

{% macro default__get_columns_in_relation(relation) -%}
  {{ exceptions.raise_not_implemented(
    'get_columns_in_relation macro not implemented for adapter '+adapter.type()) }}
{% endmacro %}