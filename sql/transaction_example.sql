BEGIN;

INSERT INTO inspections (
    date,
    time_slot,
    site,
    zone,
    worker_name,
    ppe_type,
    is_wearing
)
VALUES (
    '2026-06-02',
    '오후',
    '현장1',
    '고소작업구역',
    '트랜잭션테스트작업자',
    '랜야드',
    false
)
RETURNING inspection_id;

-- 실제 Python 코드에서는 RETURNING 받은 inspection_id를 violation_logs에 사용한다.
-- SQL 예시에서는 가장 최근 inspection_id를 사용한다.

INSERT INTO violation_logs (
    inspection_id,
    worker_name,
    site,
    zone,
    reason
)
VALUES (
    currval('inspections_inspection_id_seq'),
    '트랜잭션테스트작업자',
    '현장1',
    '고소작업구역',
    '랜야드 미착용'
);

COMMIT;