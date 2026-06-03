try:
    from app.database import get_connection
except ModuleNotFoundError:
    from database import get_connection
    
def insert_inspection_with_transaction(entry: dict) -> None:
    conn = get_connection()

    try:
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO inspections (
                date,
                time_slot,
                site,
                zone,
                worker_name,
                ppe_type,
                is_wearing
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING inspection_id;
            """,
            (
                entry.get("date"),
                entry.get("time_slot"),
                entry.get("site"),
                entry.get("zone"),
                entry.get("worker_name"),
                entry.get("ppe_type"),
                entry.get("is_wearing"),
            ),
        )

        inspection_id = cur.fetchone()[0]

        if entry.get("is_wearing") is False:
            cur.execute(
                """
                INSERT INTO violation_logs (
                    inspection_id,
                    worker_name,
                    site,
                    zone,
                    reason
                )
                VALUES (%s, %s, %s, %s, %s);
                """,
                (
                    inspection_id,
                    entry.get("worker_name"),
                    entry.get("site"),
                    entry.get("zone"),
                    "PPE 미착용",
                ),
            )

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        cur.close()
        conn.close()