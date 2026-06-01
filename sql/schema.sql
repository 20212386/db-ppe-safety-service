CREATE TABLE inspections (
    inspection_id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    time_slot VARCHAR(30),
    site VARCHAR(100),
    zone VARCHAR(100),
    worker_name VARCHAR(50),
    ppe_type VARCHAR(50),
    is_wearing BOOLEAN NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE violation_logs (
    violation_id SERIAL PRIMARY KEY,
    inspection_id INT REFERENCES inspections(inspection_id),
    worker_name VARCHAR(50),
    site VARCHAR(100),
    zone VARCHAR(100),
    reason VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);