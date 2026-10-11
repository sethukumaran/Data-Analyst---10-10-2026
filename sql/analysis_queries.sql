
-- Tech Support Analysis - SQLite


-- 1. Overall KPI
SELECT COUNT(*) AS total_conversations,
       ROUND(AVG(resolution_minutes),2) AS avg_resolution_minutes,
       MIN(resolution_minutes) AS min_resolution_minutes,
       MAX(resolution_minutes) AS max_resolution_minutes,
       ROUND(AVG(CASE WHEN issue_status='Resolved' THEN 1.0 ELSE 0 END)*100,2) AS direct_resolution_rate,
       ROUND(AVG(CASE WHEN issue_status IN ('Resolved','Resolved after follow-up') THEN 1.0 ELSE 0 END)*100,2) AS eventual_resolution_rate
FROM tech_support;

-- 2. Issue volume
SELECT customer_issue, COUNT(*) AS conversations,
       ROUND(COUNT(*)*100.0/(SELECT COUNT(*) FROM tech_support),2) AS share_pct
FROM tech_support
GROUP BY customer_issue ORDER BY conversations DESC;

-- 3. Category performance
SELECT issue_category, COUNT(*) AS conversations,
       ROUND(AVG(resolution_minutes),2) AS avg_resolution_minutes,
       ROUND(AVG(CASE WHEN issue_status='Escalated' THEN 1.0 ELSE 0 END)*100,2) AS escalation_rate_pct,
       ROUND(AVG(CASE WHEN issue_status='Pending' THEN 1.0 ELSE 0 END)*100,2) AS pending_rate_pct
FROM tech_support
GROUP BY issue_category ORDER BY avg_resolution_minutes DESC;

-- 4. Status mix
SELECT issue_status, COUNT(*) AS conversations,
       ROUND(COUNT(*)*100.0/(SELECT COUNT(*) FROM tech_support),2) AS share_pct,
       ROUND(AVG(resolution_minutes),2) AS avg_resolution_minutes
FROM tech_support GROUP BY issue_status ORDER BY conversations DESC;

-- 5. Issue-level resolution and escalation
SELECT customer_issue, COUNT(*) AS conversations,
       ROUND(AVG(resolution_minutes),2) AS avg_resolution_minutes,
       ROUND(AVG(CASE WHEN issue_status='Escalated' THEN 1.0 ELSE 0 END)*100,2) AS escalation_rate_pct,
       ROUND(AVG(CASE WHEN issue_status='Resolved after follow-up' THEN 1.0 ELSE 0 END)*100,2) AS followup_rate_pct
FROM tech_support
GROUP BY customer_issue ORDER BY escalation_rate_pct DESC;

-- 6. Response performance
SELECT tech_response, COUNT(*) AS conversations,
       ROUND(AVG(resolution_minutes),2) AS avg_resolution_minutes
FROM tech_support
GROUP BY tech_response ORDER BY avg_resolution_minutes DESC;

-- 7. Category x status
SELECT issue_category, issue_status, COUNT(*) AS conversations,
       ROUND(AVG(resolution_minutes),2) AS avg_resolution_minutes
FROM tech_support
GROUP BY issue_category, issue_status
ORDER BY issue_category, conversations DESC;

-- 8. Resolution-time bands
SELECT CASE
         WHEN resolution_minutes < 30 THEN '<30 min'
         WHEN resolution_minutes < 60 THEN '30-59 min'
         WHEN resolution_minutes < 90 THEN '60-89 min'
         ELSE '90+ min'
       END AS resolution_band,
       COUNT(*) AS conversations
FROM tech_support
GROUP BY resolution_band
ORDER BY CASE resolution_band WHEN '<30 min' THEN 1 WHEN '30-59 min' THEN 2 WHEN '60-89 min' THEN 3 ELSE 4 END;

-- 9. Data quality checks
SELECT
  (SELECT COUNT(*) FROM tech_support) AS rows,
  (SELECT COUNT(DISTINCT conversation_id) FROM tech_support) AS unique_conversations,
  (SELECT COUNT(*) FROM tech_support WHERE resolution_minutes IS NULL) AS null_resolution,
  (SELECT COUNT(*) FROM tech_support WHERE customer_issue IS NULL OR tech_response IS NULL OR issue_category IS NULL OR issue_status IS NULL) AS null_business_fields;
