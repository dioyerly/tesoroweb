import os
import sqlite3

db_path = os.path.join('instance', 'tesoreria.db')

if not os.path.exists(db_path):
  print("La base de datos no existe aún. Ejecuta 'python app.py' para crearla.")
else:
  conn = sqlite3.connect(db_path)
  cursor = conn.cursor()

  columnas_requeridas = [
      ('sociedad', 'direccion', 'VARCHAR(200)'),
      ('factura_pago', 'descripcion', 'VARCHAR(255)'),
      ('usuario', 'sociedades_permitidas', "VARCHAR(255) DEFAULT '*'"),
      ('usuario', 'debe_cambiar_password', 'BOOLEAN DEFAULT 1'),
      ('factura_pago', 'nro_oc_op', 'VARCHAR(50)'),
      (
          'factura_pago',
          'forma_pago',
          "VARCHAR(50) DEFAULT 'Transferencia'",
      ),  # <--- NUEVA COLUMNA
      ('recordatorio', 'hecho', 'BOOLEAN DEFAULT 0'),
      (
          'recordatorio',
          'recurrencia',
          "VARCHAR(30) DEFAULT 'unica'",
      ),
      (
          'movimiento_bancario',
          'categoria',
          "VARCHAR(20) DEFAULT 'pago'",
      ),
      (
          'movimiento_bancario',
          'conciliado_manual',
          'BOOLEAN DEFAULT 0',
      ),
      ('factura_pago', 'numero_cheque', 'VARCHAR(50)'),
  ]
  for tabla, columna, tipo in columnas_requeridas:
    cursor.execute(f'PRAGMA table_info({tabla})')
    columnas_existentes = [info[1] for info in cursor.fetchall()]

    if columna not in columnas_existentes:
      try:
        cursor.execute(f'ALTER TABLE {tabla} ADD COLUMN {columna} {tipo}')
        print(
            f"✓ Columna '{columna}' agregada con éxito a la tabla '{tabla}'."
        )
      except Exception as e:
        print(f'❌ Error agregando {columna} a {tabla}: {e}')
    else:
      print(f"• La columna '{columna}' ya existe en la tabla '{tabla}'.")

  conn.commit()
  conn.close()
  print('Migración completada. Tu base de datos está actualizada.')