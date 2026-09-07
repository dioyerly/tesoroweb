#!/usr/bin/env python3
"""Limpia Demo (empresa_id=1) y crea datos ficticios realistas para demostración"""
import sqlite3
from datetime import datetime, timedelta

# ===== CONECTAR A SQLITE LOCAL =====
sqlite_conn = sqlite3.connect('tesoreria.db')
sqlite_cursor = sqlite_conn.cursor()

# ===== LIMPIAR EMPRESA 1 (DEMO) SOLAMENTE =====
print("Limpiando Empresa Demo Argentina S.A. (empresa_id=1)...")

# Obtener IDs de sociedad de empresa 1 para limpiar relaciones
sqlite_cursor.execute('SELECT id FROM sociedad WHERE empresa_id = 1')
sociedad_ids = [row[0] for row in sqlite_cursor.fetchall()]

# Limpiar en orden de foreign keys
sqlite_cursor.execute('DELETE FROM conciliacion_auditoria WHERE empresa_id = 1')
sqlite_cursor.execute('DELETE FROM movimiento_split WHERE movimiento_bancario_id IN (SELECT id FROM movimiento_bancario WHERE empresa_id = 1)')
sqlite_cursor.execute('DELETE FROM movimiento_bancario WHERE empresa_id = 1')
sqlite_cursor.execute('DELETE FROM conciliacion WHERE empresa_id = 1')
sqlite_cursor.execute('DELETE FROM factura_pago WHERE empresa_id = 1')
sqlite_cursor.execute('DELETE FROM recordatorio WHERE empresa_id = 1')
sqlite_cursor.execute('DELETE FROM banco_sociedad WHERE sociedad_id IN (SELECT id FROM sociedad WHERE empresa_id = 1)')
sqlite_cursor.execute('DELETE FROM proveedor WHERE empresa_id = 1')
sqlite_cursor.execute('DELETE FROM usuario WHERE empresa_id = 1')
sqlite_cursor.execute('DELETE FROM sociedad WHERE empresa_id = 1')

print("✓ Empresa Demo limpiada\n")

# ===== CREAR NUEVOS DATOS DE DEMO =====
print("Creando datos de Demo realistas...\n")

# 1. Crear Sociedades para Demo
demo_sociedades = [
    {'nombre': 'Obra Comercial Centro', 'cuit': '30-11111111-1', 'empresa_id': 1},
    {'nombre': 'Reforma Residencial Norte', 'cuit': '30-22222222-2', 'empresa_id': 1},
]

for soc in demo_sociedades:
    sqlite_cursor.execute(
        'INSERT INTO sociedad (nombre, cuit, empresa_id) VALUES (?, ?, ?)',
        (soc['nombre'], soc['cuit'], soc['empresa_id'])
    )

sqlite_conn.commit()

# Obtener IDs de las nuevas sociedades
sqlite_cursor.execute('SELECT id FROM sociedad WHERE empresa_id = 1')
sociedad_ids = {row[0]: row[0] for row in sqlite_cursor.fetchall()}

print(f"✓ {len(sociedad_ids)} Sociedades creadas")

# 2. Crear Bancos/Cuentas para Demo
sqlite_cursor.execute('SELECT id FROM sociedad WHERE empresa_id = 1 LIMIT 1')
primera_sociedad = sqlite_cursor.fetchone()[0]

demo_bancos = [
    {'sociedad_id': primera_sociedad, 'nombre_banco': 'Banco de la Nación', 'cbu': '0120000100012345678901'},
    {'sociedad_id': primera_sociedad, 'nombre_banco': 'Banco Provincia', 'cbu': '0980750008098754321098'},
]

for banco in demo_bancos:
    sqlite_cursor.execute(
        'INSERT INTO banco_sociedad (sociedad_id, nombre_banco, cbu) VALUES (?, ?, ?)',
        (banco['sociedad_id'], banco['nombre_banco'], banco['cbu'])
    )

sqlite_conn.commit()
print(f"✓ {len(demo_bancos)} Cuentas bancarias creadas")

# 3. Crear Proveedores de Demo
demo_proveedores = [
    {'nombre': 'Hormigonera Central SA', 'empresa_id': 1, 'cuit': '30-12345678-1'},
    {'nombre': 'Aceros y Metales S.A.', 'empresa_id': 1, 'cuit': '30-87654321-0'},
    {'nombre': 'Herramientas ABC', 'empresa_id': 1, 'cuit': '30-11223344-5'},
    {'nombre': 'Pinturas y Recubrimientos', 'empresa_id': 1, 'cuit': '30-44556677-8'},
    {'nombre': 'Seguridad Industrial', 'empresa_id': 1, 'cuit': '30-99887766-2'},
]

for prov in demo_proveedores:
    sqlite_cursor.execute(
        'INSERT INTO proveedor (nombre, empresa_id, cuit) VALUES (?, ?, ?)',
        (prov['nombre'], prov['empresa_id'], prov['cuit'])
    )

sqlite_conn.commit()
print(f"✓ {len(demo_proveedores)} Proveedores creados")

# 4. Crear Facturas/Pagos de Demo
sqlite_cursor.execute('SELECT id FROM proveedor WHERE empresa_id = 1')
proveedor_ids = [row[0] for row in sqlite_cursor.fetchall()]

sqlite_cursor.execute('SELECT id FROM sociedad WHERE empresa_id = 1 LIMIT 1')
sociedad_para_facturas = sqlite_cursor.fetchone()[0]

demo_facturas = [
    {'empresa_id': 1, 'sociedad_id': sociedad_para_facturas, 'proveedor_id': proveedor_ids[0], 'nro_factura': 'FA-0001', 'monto': 15000.00, 'fecha_vencimiento': (datetime.now() - timedelta(days=30)).date(), 'estado': 'sin_pagar'},
    {'empresa_id': 1, 'sociedad_id': sociedad_para_facturas, 'proveedor_id': proveedor_ids[1], 'nro_factura': 'FA-0002', 'monto': 8500.50, 'fecha_vencimiento': (datetime.now() - timedelta(days=25)).date(), 'estado': 'pagado'},
    {'empresa_id': 1, 'sociedad_id': sociedad_para_facturas, 'proveedor_id': proveedor_ids[2], 'nro_factura': 'FA-0003', 'monto': 3200.00, 'fecha_vencimiento': (datetime.now() - timedelta(days=20)).date(), 'estado': 'pagado'},
    {'empresa_id': 1, 'sociedad_id': sociedad_para_facturas, 'proveedor_id': proveedor_ids[3], 'nro_factura': 'FA-0004', 'monto': 12500.00, 'fecha_vencimiento': (datetime.now() - timedelta(days=15)).date(), 'estado': 'sin_pagar'},
    {'empresa_id': 1, 'sociedad_id': sociedad_para_facturas, 'proveedor_id': proveedor_ids[4], 'nro_factura': 'FA-0005', 'monto': 5000.00, 'fecha_vencimiento': (datetime.now() - timedelta(days=10)).date(), 'estado': 'pagado'},
    {'empresa_id': 1, 'sociedad_id': sociedad_para_facturas, 'proveedor_id': proveedor_ids[0], 'nro_factura': 'FA-0006', 'monto': 22000.00, 'fecha_vencimiento': (datetime.now() - timedelta(days=5)).date(), 'estado': 'sin_pagar'},
]

for fact in demo_facturas:
    sqlite_cursor.execute(
        'INSERT INTO factura_pago (empresa_id, sociedad_id, proveedor_id, nro_factura, monto, fecha_vencimiento, estado) VALUES (?, ?, ?, ?, ?, ?, ?)',
        (fact['empresa_id'], fact['sociedad_id'], fact['proveedor_id'], fact['nro_factura'], fact['monto'], fact['fecha_vencimiento'], fact['estado'])
    )

sqlite_conn.commit()
print(f"✓ {len(demo_facturas)} Facturas/Pagos creadas")

# 5. Crear Movimientos Bancarios de Demo (para practicar conciliación)
import hashlib

demo_movimientos = [
    {'fecha': (datetime.now() - timedelta(days=28)).date(), 'monto': 15000.00, 'tipo': 'debito', 'descripcion': 'HORMIGONERA CENTRAL - FA-0001'},
    {'fecha': (datetime.now() - timedelta(days=23)).date(), 'monto': 8500.50, 'tipo': 'debito', 'descripcion': 'ACEROS Y METALES - FA-0002'},
    {'fecha': (datetime.now() - timedelta(days=18)).date(), 'monto': 3200.00, 'tipo': 'debito', 'descripcion': 'HERRAMIENTAS ABC - FA-0003'},
    {'fecha': (datetime.now() - timedelta(days=12)).date(), 'monto': 50000.00, 'tipo': 'credito', 'descripcion': 'TRANSFERENCIA ENTRADA - CLIENTE XYZ'},
    {'fecha': (datetime.now() - timedelta(days=8)).date(), 'monto': 5000.00, 'tipo': 'debito', 'descripcion': 'SEGURIDAD INDUSTRIAL - FA-0005'},
]

for mov in demo_movimientos:
    hash_text = f"{mov['fecha']}|{mov['monto']:.2f}|{mov['tipo']}|{mov['descripcion']}"
    hash_dedup = hashlib.sha256(hash_text.encode()).hexdigest()

    sqlite_cursor.execute(
        'INSERT INTO movimiento_bancario (empresa_id, fecha, monto, tipo, descripcion, hash_dedup, estado, categoria, archivo_origen) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (1, mov['fecha'], mov['monto'], mov['tipo'], mov['descripcion'], hash_dedup, 'sin_conciliar', 'pago', 'DEMO_INICIAL')
    )

sqlite_conn.commit()
print(f"✓ {len(demo_movimientos)} Movimientos Bancarios creados")

# 6. Crear Usuarios Admin para Demo
from werkzeug.security import generate_password_hash

demo_usuarios = [
    {'email': 'demo@tesoreria.com', 'nombre': 'Demo Administrador', 'empresa_id': 1, 'rol': 'Administrador', 'cargo': 'Admin', 'password': 'Demo1234'},
]

for user in demo_usuarios:
    password_hash = generate_password_hash(user['password'])

    sqlite_cursor.execute(
        'INSERT INTO usuario (email, nombre, empresa_id, rol, cargo, password_hash, activo, debe_cambiar_password) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        (user['email'], user['nombre'], user['empresa_id'], user['rol'], user['cargo'], password_hash, True, False)
    )

sqlite_conn.commit()
print(f"✓ {len(demo_usuarios)} Usuarios Demo creados")

sqlite_conn.close()

print("\n" + "="*60)
print("✓ DEMO COMPLETAMENTE RECREADA")
print("="*60)
print(f"\n📊 Datos de Demo cargados:")
print(f"  • 2 Sociedades")
print(f"  • 2 Cuentas Bancarias")
print(f"  • 5 Proveedores")
print(f"  • 6 Facturas/Pagos")
print(f"  • 5 Movimientos Bancarios (para practicar conciliación)")
print(f"  • 1 Usuario Administrador")
print(f"\n🔑 Usuario para Demo:")
print(f"  Email: demo@tesoreria.com")
print(f"  Contraseña: Demo1234")
print(f"\n⚠️  IMPORTANTE:")
print(f"  ✓ EMPRENDIMIENTOS Y ESTRUCTURAS (empresa_id=2) NO fue tocada")
print(f"  ✓ Todos tus datos reales están intactos")
