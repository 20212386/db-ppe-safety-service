-- 1. 전체 점검 기록 조회
SELECT *
FROM inspections
ORDER BY created_at DESC;

-- 2. 미착용 기록 조회
SELECT
    inspection_id,
    date,
    time_slot,
    site,
    zone,
    worker_name,
    ppe_type,
    created_at
FROM inspections
WHERE is_wearing = false
ORDER BY created_at DESC;

-- 3. 날짜별 PPE 준수율
SELECT
    date,
    COUNT(*) AS total_count,
    SUM(CASE WHEN is_wearing = true THEN 1 ELSE 0 END) AS wearing_count,
    ROUND(
        SUM(CASE WHEN is_wearing = true THEN 1 ELSE 0 END)::numeric
        / COUNT(*) * 100,
        2
    ) AS compliance_rate
FROM inspections
GROUP BY date
ORDER BY date;

-- 4. 현장별 위반 건수
SELECT
    site,
    COUNT(*) AS violation_count
FROM inspections
WHERE is_wearing = false
GROUP BY site
ORDER BY violation_count DESC;

-- 5. 구역별 위반 건수
SELECT
    zone,
    COUNT(*) AS violation_count
FROM inspections
WHERE is_wearing = false
GROUP BY zone
ORDER BY violation_count DESC;

-- 6. PPE 종류별 미착용 건수
SELECT
    ppe_type,
    COUNT(*) AS missed_count
FROM inspections
WHERE is_wearing = false
GROUP BY ppe_type
ORDER BY missed_count DESC;

-- 7. 시간대별 위반 건수
SELECT
    time_slot,
    COUNT(*) AS violation_count
FROM inspections
WHERE is_wearing = false
GROUP BY time_slot
ORDER BY violation_count DESC;

-- 8. 위반 로그와 점검 기록 JOIN
SELECT
    v.violation_id,
    i.date,
    i.time_slot,
    v.site,
    v.zone,
    v.worker_name,
    i.ppe_type,
    v.reason,
    v.created_at
FROM violation_logs v
JOIN inspections i
ON v.inspection_id = i.inspection_id
ORDER BY v.created_at DESC;