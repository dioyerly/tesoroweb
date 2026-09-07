#!/usr/bin/env python3
"""Actualiza password del usuario demo@tesoreria.com en PostgreSQL"""
import psycopg2
from urllib.parse import urlparse
from werkzeug.security import generate_password_hash

db_url = "postgresql://tesoreria_db_9jq2_user:sRS7vnaC4eUmyq22LihDk8NUjCPg7xnV@dpg-dafcrqajnfac73bjt5hg-a.oregon-postgres.render.com:5432/tesoreria_db_9jq2"

parsed = urlparse(db_url)
pg_conn = psycopg2.connect(
    host=parsed.hostname, port=5432,
    user=parsed.username, password=parsed.password,
    database=parsed.path.lstrip('/')
)

password = "Demo1234"
password_hash = generate_password_hash(password)

pg_cursor = pg_conn.cursor()

# Primero, eliminar cualquier usuario demo anterior incorrecto
pg_cursor.execute('DELETE FROM usuario WHERE email = %s AND empresa_id = 1', ('demo@tesoreria.com',))

# Luego, insertar el usuario demo correcto
pg_cursor.execute("""
    INSERT INTO usuario (email, nombre, empresa_id, rol, cargo, password_hash, activo, debe_cambiar_password)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (email) DO UPDATE SET password_hash = EXCLUDED.password_hash
""", (
    'demo@tesoreria.com',
    'Demo Administrador',
    1,
    'Administrador',
    'Admin',
    password_hash,
    True,
    False
))

pg_conn.commit()

print("✓ Usuario demo@tesoreria.com actualizado")
print(f"  Email: demo@tesoreria.com")
print(f"  Contraseña: Demo1234")
print(f"  Empresa: Empresa Demo Argentina S.A.")

pg_cursor.close()
pg_conn.close()
