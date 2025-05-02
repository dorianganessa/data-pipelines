SELECT
  *
FROM
  {{ source('real_estate', 'properties') }}
WHERE
  price < 10000000
  AND square_meters < 10000
