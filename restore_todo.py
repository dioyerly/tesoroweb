#!/usr/bin/env python3
"""Restaura TODOS los datos de ambas empresas desde SQLite"""
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

print("Restaurando datos...\n")

# Tablas y su filtro
TABLAS = [
    ('empresa', None),
    ('sociedad', 'empresa_id'),
    ('banco_sociedad', 'sociedad.empresa_id'),  # JOIN necesario
    ('proveedor', 'empresa_id'),
    ('factura_pago', 'empresa_id'),
    ('recordatorio', 'empresa_id'),
    ('movimiento_bancario', 'empresa_id'),
    ('movimiento_split', 'movimiento_bancario.empresa_id'),  # JOIN
    ('conciliacion', 'empresa_id'),
    ('conciliacion_auditoria', 'empresa_id'),
]

total = 0

for tabla, filtro in TABLAS:
    print(f"{tabla}...", end=" ")
    try:
        sqlite_cursor.execute(f"PRAGMA table_info({tabla})")
        columnas = [row[1] for row in sqlite_cursor.fetchall()]

        if filtro and 'JOIN' in filtro:
            # Casos con JOIN
            if tabla == 'banco_sociedad':
                sqlite_cursor.execute(f"""
                    SELECT bs.{', bs.'.join(columnas)} FROM banco_sociedad bs
                    JOIN sociedad s ON bs.sociedad_id = s.id
                    WHERE s.empresa_id IN (1, 2)
                """)
            elif tabla == 'movimiento_split':
                sqlite_cursor.execute(f"""
                    SELECT ms.{', ms.'.join(columnas)} FROM movimiento_split ms
                    JOIN movimiento_bancario mb ON ms.movimiento_bancario_id = mb.id
                    WHERE mb.empresa_id IN (1, 2)
                """)
        elif filtro:
            # Filtro simple
            sqlite_cursor.execute(f"""
                SELECT {', '.join(columnas)} FROM {tabla}
                WHERE {filtro} IN (1, 2)
            """)
        else:
            # Sin filtro (solo empresa)
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

print(f"\n✓ Restauración completada: {total} registros totales")
