#!/usr/bin/env python3
"""
Script para migrar datos de SQLite a PostgreSQL
Uso: python migrate_to_postgres.py <DATABASE_URL>
"""
import sqlite3
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

if len(sys.argv) < 2:
    print("Uso: python migrate_to_postgres.py <DATABASE_URL>")
    sys.exit(1)

postgres_url = sys.argv[1]
sqlite_path = 'tesoreria.db'

print(f"Conectando a SQLite: {sqlite_path}")
sqlite_conn = sqlite3.connect(sqlite_path)
sqlite_cursor = sqlite_conn.cursor()

print(f"Conectando a PostgreSQL: {postgres_url[:50]}...")
pg_engine = create_engine(postgres_url)

with pg_engine.connect() as conn:
    conn.execute(text("SELECT 1"))
    print("✓ PostgreSQL conectado")

sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = sqlite_cursor.fetchall()

print(f"\nEncontradas {len(tables)} tablas")

for table_name, in tables:
    if table_name.startswith('sqlite_'):
        continue

    sqlite_cursor.execute(f"SELECT * FROM {table_name}")
    columns = [desc[0] for desc in sqlite_cursor.description]
    rows = sqlite_cursor.fetchall()

    if not rows:
        print(f"  {table_name}: vacía")
        continue

    print(f"  {table_name}: {len(rows)} registros")

    placeholders = ', '.join(['%s'] * len(columns))
    insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"

    with pg_engine.begin() as conn:
        for row in rows:
            try:
                conn.execute(text(insert_sql), row)
            except Exception as e:
                print(f"    Error en {table_name}: {e}")

sqlite_conn.close()
print("\n✓ Migración completada")
