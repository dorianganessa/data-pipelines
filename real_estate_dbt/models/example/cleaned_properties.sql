{{ config(
    materialized='incremental',
    unique_key='url'
) }}

SELECT
  *
FROM
  {{ ref('properties') }}
WHERE
  {% if is_incremental() %}
    created_at BETWEEN '{{ this.start_date }}' AND '{{ this.end_date }}'
  {% else %}
    created_at >= '2020-01-01'
  {% endif %}
  AND price < 10000000
