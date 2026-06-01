UPDATE inspections
SET site = CASE
    WHEN inspection_id % 3 = 1 THEN '현장1'
    WHEN inspection_id % 3 = 2 THEN '현장2'
    ELSE '현장3'
END
WHERE site IS NULL OR TRIM(site) = '';