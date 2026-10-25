-- SQLite-compatible cleaning layer for community.csv.
-- Load the source file into raw_community with all columns stored as TEXT.
DROP VIEW IF EXISTS clean_community;

CREATE VIEW clean_community AS
SELECT DISTINCT
    date(trim(date)) AS date,
    lower(trim(dimension)) AS dimension,
    lower(trim(dimension_value)) AS dimension_value,
    CAST(trim(events) AS INTEGER) AS events,
    CAST(trim(tokens) AS INTEGER) AS tokens,
    CAST(trim(cost) AS REAL) AS cost,
    CAST(trim(contributors) AS INTEGER) AS contributors,
    CAST(trim(success) AS INTEGER) AS success,
    CAST(NULLIF(trim(quality_avg), '') AS REAL) AS quality_avg,
    CAST(NULLIF(trim(latency_avg_ms), '') AS REAL) AS latency_avg_ms
FROM raw_community
WHERE date(trim(date)) IS NOT NULL
  AND lower(trim(dimension)) IN ('total', 'model', 'platform', 'provider', 'use_case')
  AND NULLIF(trim(dimension_value), '') IS NOT NULL
  AND trim(events) != ''
  AND trim(events) NOT GLOB '*[^0-9]*'
  AND CAST(trim(events) AS INTEGER) >= 0
  AND trim(tokens) != ''
  AND trim(tokens) NOT GLOB '*[^0-9]*'
  AND CAST(trim(tokens) AS INTEGER) >= 0
  AND trim(cost) != ''
  AND trim(cost) GLOB '*[0-9]*'
  AND trim(cost) NOT GLOB '*[^0-9.]*'
  AND length(trim(cost)) - length(replace(trim(cost), '.', '')) <= 1
  AND CAST(trim(cost) AS REAL) >= 0
  AND trim(contributors) != ''
  AND trim(contributors) NOT GLOB '*[^0-9]*'
  AND CAST(trim(contributors) AS INTEGER) >= 0
  AND trim(success) != ''
  AND trim(success) NOT GLOB '*[^0-9]*';

-- Important: dimensions are overlapping daily rollups. For overall time trends,
-- filter dimension='total'. Never sum across all dimensions.
