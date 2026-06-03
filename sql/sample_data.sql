INSERT INTO inspections (
    date,
    time_slot,
    site,
    zone,
    worker_name,
    ppe_type,
    is_wearing
)
SELECT
    DATE '2026-05-20' + ((g - 1) % 15),
    CASE
        WHEN g % 3 = 1 THEN '오전'
        WHEN g % 3 = 2 THEN '점심직후'
        ELSE '오후'
    END,
    CASE
        WHEN g % 3 = 1 THEN '현장1'
        WHEN g % 3 = 2 THEN '현장2'
        ELSE '현장3'
    END,
    CASE
        WHEN g % 4 = 1 THEN '고소작업구역'
        WHEN g % 4 = 2 THEN '절단작업구역'
        WHEN g % 4 = 3 THEN '자재운반구역'
        ELSE '설비점검구역'
    END,
    '작업자' || g,
    CASE
        WHEN g % 3 = 1 THEN '안전모'
        WHEN g % 3 = 2 THEN '랜야드'
        ELSE '장갑'
    END,
    CASE
        WHEN g % 10 IN (0, 1, 2, 3) THEN false
        ELSE true
    END
FROM generate_series(1, 1000) AS g;