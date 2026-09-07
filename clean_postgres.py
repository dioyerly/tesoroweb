#!/usr/bin/env python3
"""Limpia todas las tablas de PostgreSQL"""
import sys
import psycopg2
from urllib.parse import urlparse

if len(sys.argv) < 2:
    print("Uso: python clean_postgres.py <DATABASE_URL>")
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

print("Conectando a PostgreSQL...")
pg_conn = psycopg2.connect(**pg_config)
pg_cursor = pg_conn.cursor()

print("Obteniendo lista de tablas...")
pg_cursor.execute("""
    SELECT tablename FROM pg_tables
    WHERE schemaname='public'
""")
tables = [row[0] for row in pg_cursor.fetchall()]

print(f"Encontradas {len(tables)} tablas")

if not tables:
    print("No hay tablas que limpiar")
    pg_conn.close()
    sys.exit(0)

print("\nLimpiando tablas...")
for table in tables:
    print(f"  TRUNCATE {table}...", end="")
    try:
        pg_cursor.execute(f"TRUNCATE TABLE {table} CASCADE")
        pg_conn.commit()
        print(" ✓")
    except Exception as e:
        pg_conn.rollback()
        print(f" ✗ {str(e)[:50]}")

pg_cursor.close()
pg_conn.close()

print("\n✓ Limpieza completada")
