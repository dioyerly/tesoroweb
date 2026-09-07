#!/usr/bin/env python3
"""Restaura Demo (empresa_id=1) desde SQLite a PostgreSQL"""
import sqlite3
import psycopg2
from urllib.parse import urlparse

db_url = "postgresql://tesoreria_db_9jq2_user:sRS7vnaC4eUmyq22LihDk8NUjCPg7xnV@dpg-dafcrqajnfac73bjt5hg-a.oregon-postgres.render.com:5432/tesoreria_db_9jq2"

print("Conectando a bases de datos...")
sqlite_conn = sqlite3.connect('tesoreria.db')
sqlite_cursor = sqlite_conn.cursor()

parsed = urlparse(db_url)
pg_conn = psycopg2.connect(
    host=parsed.hostname, port=5432,
    user=parsed.username, password=parsed.password,
    database=parsed.path.lstrip('/')
)

print("Limpiando Demo en PostgreSQL (empresa_id=1)...\n")

# Limpiar empresa 1 en PostgreSQL
pg_cursor = pg_conn.cursor()
pg_cursor.execute('DELETE FROM conciliacion_auditoria WHERE empresa_id = 1')
pg_cursor.execute('DELETE FROM movimiento_split WHERE movimiento_bancario_id IN (SELECT id FROM movimiento_bancario WHERE empresa_id = 1)')
pg_cursor.execute('DELETE FROM movimiento_bancario WHERE empresa_id = 1')
pg_cursor.execute('DELETE FROM conciliacion WHERE empresa_id = 1')
pg_cursor.execute('DELETE FROM factura_pago WHERE empresa_id = 1')
pg_cursor.execute('DELETE FROM recordatorio WHERE empresa_id = 1')
pg_cursor.execute('DELETE FROM banco_sociedad WHERE sociedad_id IN (SELECT id FROM sociedad WHERE empresa_id = 1)')
pg_cursor.execute('DELETE FROM proveedor WHERE empresa_id = 1')
pg_cursor.execute('DELETE FROM usuario WHERE empresa_id = 1')
pg_cursor.execute('DELETE FROM sociedad WHERE empresa_id = 1')
pg_conn.commit()

print("Restaurando Demo desde SQLite...\n")

# Tablas a restaurar (empresa 1 solamente)
TABLAS = [
    'empresa',
    'sociedad',
    'banco_sociedad',
    'proveedor',
    'factura_pago',
    'recordatorio',
    'movimiento_bancario',
    'movimiento_split',
    'conciliacion',
    'conciliacion_auditoria',
    'usuario',
]

total = 0

for tabla in TABLAS:
    print(f"{tabla}...", end=" ", flush=True)
    try:
        sqlite_cursor.execute(f"PRAGMA table_info({tabla})")
        columnas = [row[1] for row in sqlite_cursor.fetchall()]

        # Para usuario y empresa, filtrar por empresa_id
        if tabla == 'empresa':
            sqlite_cursor.execute(f"SELECT {', '.join(columnas)} FROM {tabla} WHERE id = 1")
        elif tabla in ('usuario', 'sociedad', 'proveedor', 'factura_pago', 'recordatorio', 'movimiento_bancario', 'conciliacion', 'conciliacion_auditoria'):
            sqlite_cursor.execute(f"SELECT {', '.join(columnas)} FROM {tabla} WHERE empresa_id = 1")
        elif tabla == 'banco_sociedad':
            sqlite_cursor.execute(f"""
                SELECT bs.{', bs.'.join(columnas)} FROM {tabla} bs
                JOIN sociedad s ON bs.sociedad_id = s.id
                WHERE s.empresa_id = 1
            """)
        elif tabla == 'movimiento_split':
            sqlite_cursor.execute(f"""
                SELECT ms.{', ms.'.join(columnas)} FROM {tabla} ms
                JOIN movimiento_bancario mb ON ms.movimiento_bancario_id = mb.id
                WHERE mb.empresa_id = 1
            """)
        else:
            sqlite_cursor.execute(f"SELECT {', '.join(columnas)} FROM {tabla}")

        rows = sqlite_cursor.fetchall()

        if rows:
            pg_cursor = pg_conn.cursor()
            placeholders = ', '.join(['%s'] * len(columnas))
            sql = f"INSERT INTO {tabla} ({', '.join(columnas)}) VALUES ({placeholders}) ON CONFLICT DO NOTHING"

            for row in rows:
                try:
                    pg_cursor.execute(sql, row)
                except:
                    pass

            pg_conn.commit()
            pg_cursor.close()
            total += len(rows)
            print(f"✓ {len(rows)}")
        else:
            print("vacía")

    except Exception as e:
        print(f"✗ {str(e)[:50]}")

sqlite_conn.close()
pg_conn.close()

print(f"\n✓ Demo restaurada: {total} registros totales")
print("\nAhora hace Redeploy en Render para que los cambios aparezcan en la web.")
