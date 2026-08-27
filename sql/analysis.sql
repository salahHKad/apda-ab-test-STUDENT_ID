-- DuckDB analysis queries for the landing page A/B test.
-- Both queries run against the "clean_ab_data" view, which scripts/run_sql.py
-- registers from data/processed/clean_data.parquet before running these.
-- "group" is a reserved SQL word, so it is quoted throughout.
 
-- ============================================================
-- @name: group_summary
-- Users, conversions, and conversion rate for each experiment group.
-- ============================================================
SELECT
    "group",
    count(*) AS users,
    SUM(converted) AS conversions,
    ROUND(SUM(converted)*1.0/COUNT(*),4) AS conversion_rate
    FROM clean_ab_data
    GROUP BY "group"
    ORDER BY "group";
    
-- ============================================================
-- @name: daily_conversion
-- Users, conversions, and conversion rate for each group, per day.
-- ============================================================

SELECT 
    experiment_date,
    "group",
    COUNT(*) AS users,
    SUM(converted) AS conversions,
    ROUND(SUM(converted)*1.0/COUNT(*),4) AS conversion_rate

FROM clean_ab_data
GROUP BY experiment_date, "group"
ORDER BY experiment_date, "group";