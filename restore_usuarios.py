#!/usr/bin/env python3
"""Restaura usuarios desde SQLite a PostgreSQL"""
import sqlite3
import psycopg2
from urllib.parse import urlparse

db_url = "postgresql://tesoreria_db_9jq2_user:sRS7vnaC4eUmyq22LihDk8NUjCPg7xnV@dpg-dafcrqajnfac73bjt5hg-a.oregon-postgres.render.com:5432/tesoreria_db_9jq2"

print("Leyendo usuarios de SQLite...")
sqlite_conn = sqlite3.connect('tesoreria.db')
sqlite_cursor = sqlite_conn.cursor()
sqlite_cursor.execute('SELECT id, nombre, email, password_hash, rol, cargo, empresa_id, activo FROM usuario')
usuarios = sqlite_cursor.fetchall()
sqlite_conn.close()

print(f"Encontrados {len(usuarios)} usuarios")

print("Conectando a PostgreSQL...")
parsed = urlparse(db_url)
pg_conn = psycopg2.connect(
    host=parsed.hostname,
    port=5432,
    user=parsed.username,
    password=parsed.password,
    database=parsed.path.lstrip('/')
)

print("Restaurando usuarios...")
count = 0
for usuario in usuarios:
    id, nombre, email, password_hash, rol, cargo, empresa_id, activo = usuario
    activo_bool = bool(activo)
    pg_cursor = pg_conn.cursor()
    try:
        pg_cursor.execute("""
            INSERT INTO usuario (id, nombre, email, password_hash, rol, cargo, empresa_id, activo)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, (id, nombre, email, password_hash, rol, cargo, empresa_id, activo_bool))
        pg_conn.commit()
        count += 1
        print(f"  ✓ {email}")
    except Exception as e:
        pg_conn.rollback()
        print(f"  ✗ {email}: {str(e)[:60]}")
    finally:
        pg_cursor.close()

pg_conn.close()
print(f"\n✓ {count} usuarios restaurados de {len(usuarios)}")
