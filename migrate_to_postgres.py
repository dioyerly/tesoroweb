#!/usr/bin/env python3
"""Migra datos de SQLite a PostgreSQL"""
import sqlite3
import sys
import psycopg2
from urllib.parse import urlparse

if len(sys.argv) < 2:
    print("Uso: python migrate_to_postgres.py <DATABASE_URL>")
    sys.exit(1)

db_url = sys.argv[1]
parsed = urlparse(db_url)

pg_config = {
    'host': parsed.hostname,
    'port': parsed.port or 5432,
    'user': parsed.username,
    'password': parsed.password,
    'database': parsed.path.lstrip('/')
}

print(f"Conectando a SQLite: tesoreria.db")
sqlite_conn = sqlite3.connect('tesoreria.db')
sqlite_cursor = sqlite_conn.cursor()

print(f"Conectando a PostgreSQL...")
pg_conn = psycopg2.connect(**pg_config)
pg_cursor = pg_conn.cursor()
print("✓ Conectado")

sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [row[0] for row in sqlite_cursor.fetchall()]
tables = [t for t in tables if not t.startswith('sqlite_')]

print(f"\nEncontradas {len(tables)} tablas\n")

for table_name in tables:
    sqlite_cursor.execute(f"SELECT * FROM {table_name}")
    columns = [desc[0] for desc in sqlite_cursor.description]
    rows = sqlite_cursor.fetchall()

    if not rows:
        print(f"  {table_name}: vacía")
        continue

    print(f"  {table_name}: migrando {len(rows)} registros...", end='')

    placeholders = ','.join(['%s'] * len(columns))
    insert_sql = f"INSERT INTO {table_name} ({','.join(columns)}) VALUES ({placeholders})"

    try:
        for row in rows:
            pg_cursor.execute(insert_sql, row)
        pg_conn.commit()
        print(" ✓")
    except Exception as e:
        pg_conn.rollback()
        print(f" ✗ {str(e)[:50]}")

sqlite_conn.close()
pg_cursor.close()
pg_conn.close()

print("\n✓ Migración completada")
