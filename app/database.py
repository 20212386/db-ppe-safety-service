import os
from pathlib import Path

import pandas as pd
import psycopg2
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(ENV_PATH)

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "ppe_safety"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT", "5432"),
    )

def fetch_dataframe(query: str, params=None) -> pd.DataFrame:
    conn = get_connection()
    try:
        return pd.read_sql(query, conn, params=params)
    finally:
        conn.close()