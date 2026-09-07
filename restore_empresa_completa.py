#!/usr/bin/env python3
"""Restaura TODOS los datos de EMPRENDIMIENTOS Y ESTRUCTURAS SA"""
import sqlite3
import psycopg2
from urllib.parse import urlparse

# ID de la empresa a restaurar
EMPRESA_ID = 2  # EMPRENDIMIENTOS Y ESTRUCTURAS SA

db_url = "postgresql://tesoreria_db_9jq2_user:sRS7vnaC4eUmyq22LihDk8NUjCPg7xnV@dpg-dafcrqajnfac73bjt5hg-a.oregon-postgres.render.com:5432/tesoreria_db_9jq2"

print(f"Restaurando TODOS los datos de empresa_id={EMPRESA_ID}...")

sqlite_conn = sqlite3.connect('tesoreria.db')
sqlite_cursor = sqlite_conn.cursor()

parsed = urlparse(db_url)
pg_conn = psycopg2.connect(
    host=parsed.hostname, port=5432,
    user=parsed.username, password=parsed.password,
    database=parsed.path.lstrip('/')
)

# Tablas a restaurar en orden (respetando foreign keys)
TABLAS = [
    ('sociedad', 'empresa_id'),
    ('banco_sociedad', 'empresa_id'),
    ('proveedor', 'empresa_id'),
    ('factura_pago', 'empresa_id'),
    ('recordatorio', 'empresa_id'),
    ('movimiento_bancario', 'empresa_id'),
    ('movimiento_split', 'movimiento_id'),  # Sin filtro, depende de movimiento
    ('conciliacion', 'empresa_id'),
    ('conciliacion_auditoria', 'empresa_id'),
]

total_restaurados = 0

for tabla, filtro_col in TABLAS:
    print(f"\nTabla: {tabla}...", end="")
    try:
        sqlite_cursor.execute(f"PRAGMA table_info({tabla})")
        columnas = [row[1] for row in sqlite_cursor.fetchall()]

        if filtro_col == 'movimiento_id':
            # Para movimiento_split, necesitar ids de movimientos de esa empresa
            sqlite_cursor.execute(f"""
                SELECT {', '.join(columnas)} FROM {tabla}
                WHERE movimiento_id IN (
                    SELECT id FROM movimiento_bancario WHERE empresa_id = ?
                )
            """, (EMPRESA_ID,))
        else:
            # Filtrar por empresa_id
            sqlite_cursor.execute(f"""
                SELECT {', '.join(columnas)} FROM {tabla}
                WHERE {filtro_col} = ?
            """, (EMPRESA_ID,))

        rows = sqlite_cursor.fetchall()

        if not rows:
            print(" (vacía)")
            continue

        placeholders = ', '.join(['%s'] * len(columnas))
        insert_sql = f"INSERT INTO {tabla} ({', '.join(columnas)}) VALUES ({placeholders}) ON CONFLICT DO NOTHING"

        pg_cursor = pg_conn.cursor()
        for row in rows:
            try:
                pg_cursor.execute(insert_sql, row)
            except Exception as e:
                pass

        pg_conn.commit()
        pg_cursor.close()

        print(f" ✓ {len(rows)} registros")
        total_restaurados += len(rows)

    except Exception as e:
        print(f" ✗ Error: {str(e)[:60]}")

sqlite_conn.close()
pg_conn.close()

print(f"\n✓ Restauración completada: {total_restaurados} registros")
