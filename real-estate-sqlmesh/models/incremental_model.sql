MODEL (
  name main.cleaned_properties,
  kind INCREMENTAL_BY_TIME_RANGE (
    time_column (created_at, '%Y-%m-%d %H:%M:%S.%f')
  ),
  start '2020-01-01',
  grain (url)
);

SELECT
  *
FROM
  main.properties
WHERE
  created_at BETWEEN @start_date AND @end_date
  AND price < 10000000
  