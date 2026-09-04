#!/usr/bin/env python3
"""
Script de Seed para Datos de Demo en Tesorería App
Carga datos falsos realistas para mostrar en videos y presentaciones
"""

from app import app, db
from models import (
    Empresa, Usuario, Sociedad, BancoSociedad, Proveedor,
    FacturaPago, Recordatorio, MovimientoBancario
)
from datetime import datetime, date, timedelta
import hashlib
import random

# Datos falsos realistas
EMPRESAS_DEMO = [
    {
        "nombre": "Empresa Demo Argentina S.A.",
        "cuit": "30987654321",  # Falso
    }
]

SOCIEDADES_DATA = [
    {
        "nombre": "Constructora Centro S.R.L.",
        "cuit": "30456789012",  # Falso
        "direccion": "Av. 9 de Julio 1234, CABA",
    },
    {
        "nombre": "Servicios Logísticos S.A.",
        "cuit": "33876543210",  # Falso
        "direccion": "Ruta 5 km 35, La Matanza, Buenos Aires",
    },
    {
        "nombre": "Consultora Técnica S.R.L.",
        "cuit": "30765432109",  # Falso
        "direccion": "Balcarce 456, San Isidro, Buenos Aires",
    },
]

BANCOS_DATA = [
    ("Banco Galicia", "0070123456789012345"),
    ("Banco BBVA Argentina", "0150987654321098765"),
    ("Banco Santander Río", "0072456789012345678"),
    ("Banco ICBC", "0060789012345678901"),
]

PROVEEDORES_DATA = [
    ("Distribuidora de Materiales Hnos. García S.A.", "30123456789", "alias.garcia.1"),
    ("Aceros Inoxidables del Sur S.R.L.", "33234567890", "aceros.sur.alias"),
    ("Química Industrial Ltda.", "30345678901", "quimica.industria"),
    ("Transportes Rápidos S.A.", "30456789012", "transportes.rapidos"),
    ("Maderas y Compensados S.R.L.", "33567890123", "maderas.comp"),
    ("Pinturas Premium Argentina S.A.", "30678901234", "pinturas.premium"),
    ("Herramientas Profesionales Ltda.", "30789012345", "herramientas.prof"),
    ("Seguridad Industrial del Centro S.A.", "33890123456", "seguridad.ind"),
    ("Equipos Electromecánicos Ltda.", "30901234567", "equipos.electro"),
    ("Combustibles y Lubricantes S.R.L.", "33012345678", "combustibles.lub"),
    ("Vidrio Templado Buenos Aires S.A.", "30123456780", "vidrio.templado"),
    ("Sanitarios y Griferías S.R.L.", "33234567891", "sanitarios.grif"),
    ("Sistemas de Aire Acondicionado S.A.", "30345678902", "aire.acond"),
    ("Cables y Conductores Eléctricos Ltda.", "30456789013", "cables.conduct"),
    ("Tuberías Plásticas Premium S.R.L.", "33567890124", "tuberias.plastico"),
    ("Cerraduras y Cerrajería Ltda.", "30678901235", "cerraduras.pro"),
    ("Puertas y Ventanas Integral S.A.", "33789012346", "puertas.ventanas"),
    ("Pisos y Revestimientos Mármol S.R.L.", "30890123457", "pisos.marmol"),
    ("Estructuras Metálicas Reforzadas Ltda.", "33901234568", "estructuras.metal"),
    ("Aislantes Térmicos Nacionales S.A.", "30012345679", "aislantes.termo"),
    ("Cerámicas Decorativas Ltda.", "33123456780", "ceramicas.decor"),
    ("Tornillería Industrial Premium S.R.L.", "30234567890", "tornilleria.ind"),
]

EMPLEADOS_DATA = [
    {
        "nombre": "Juan Carlos Martínez",
        "email": "jmartinez@andamios.com",
        "cargo": "Administrador General",
        "rol": "Administrador",
    },
    {
        "nombre": "María Fernanda López",
        "email": "mlopez@andamios.com",
        "cargo": "Tesorera",
        "rol": "Operador",
    },
    {
        "nombre": "Roberto Silva",
        "email": "rsilva@andamios.com",
        "cargo": "Contador",
        "rol": "Contador",
    },
    {
        "nombre": "Ana González",
        "email": "agonzalez@andamios.com",
        "cargo": "Asistente de Tesorería",
        "rol": "Operador",
    },
    {
        "nombre": "Diego Rodríguez",
        "email": "drodriguez@andamios.com",
        "cargo": "Supervisor de Caja",
        "rol": "Supervisor",
    },
]

TIPOS_GASTOS = ["proveedor", "servicio"]
FORMAS_PAGO = ["Transferencia", "Cheque", "Efectivo"]

def generar_cuit_falso():
    """Genera un CUIT falso válido (11 dígitos)"""
    return f"30{random.randint(100000000, 999999999)}"

def generar_alias_falso():
    """Genera un alias CBU falso"""
    adjuntos = ["alias", "cbu", "cuenta", "banco", "trans"]
    palabras = random.sample(["flujo", "pago", "demo", "prueba", "test", "velocidad"], 2)
    return ".".join([adjuntos[random.randint(0, len(adjuntos)-1)]] + palabras)

def generar_nro_factura():
    """Genera un número de factura falso"""
    pv = f"{random.randint(1, 5):04d}"
    comp = f"{random.randint(1, 99999999):08d}"
    return f"{pv}-{comp}"

def generar_hash_dedup(fecha, monto, descripcion):
    """Genera hash de deduplicación"""
    s = f"{fecha}{monto}{descripcion}".encode()
    return hashlib.sha256(s).hexdigest()

def seed_database():
    """Carga todos los datos demo en la base de datos"""

    with app.app_context():
        print("[*] Iniciando seed de datos demo...")

        # 1. Crear la empresa principal
        print("\n[1] Creando empresa demo...")
        empresa_data = EMPRESAS_DEMO[0]

        # Verificar si ya existe
        empresa = Empresa.query.filter_by(cuit=empresa_data["cuit"]).first()
        if not empresa:
            empresa = Empresa(
                nombre=empresa_data["nombre"],
                cuit=empresa_data["cuit"],
                estado_suscripcion="activa"
            )
            db.session.add(empresa)
            db.session.commit()
            print(f"[OK] Empresa '{empresa.nombre}' creada")
        else:
            print(f"[INFO] Empresa '{empresa.nombre}' ya existe")

        # 2. Crear empleados
        print("\n[2] Creando empleados...")
        usuarios = []
        for emp_data in EMPLEADOS_DATA:
            usr = Usuario.query.filter_by(email=emp_data["email"]).first()
            if not usr:
                usr = Usuario(
                    empresa_id=empresa.id,
                    nombre=emp_data["nombre"],
                    email=emp_data["email"],
                    cargo=emp_data["cargo"],
                    rol=emp_data["rol"],
                    activo=True,
                    debe_cambiar_password=False,
                )
                usr.set_password("Demo1234")
                db.session.add(usr)
                usuarios.append(usr)
                print(f"  [OK] {emp_data['nombre']} ({emp_data['rol']})")

        db.session.commit()

        # 3. Crear sociedades
        print("\n[3] Creando sociedades...")
        sociedades = []
        for soc_data in SOCIEDADES_DATA:
            soc = Sociedad.query.filter_by(
                empresa_id=empresa.id,
                cuit=soc_data["cuit"]
            ).first()
            if not soc:
                soc = Sociedad(
                    empresa_id=empresa.id,
                    nombre=soc_data["nombre"],
                    cuit=soc_data["cuit"],
                    direccion=soc_data["direccion"],
                )
                db.session.add(soc)
                sociedades.append(soc)
                print(f"  [OK] {soc_data['nombre']}")

        db.session.commit()

        # 4. Crear bancos para cada sociedad
        print("\n[4] Asignando bancos a sociedades...")
        for soc in sociedades:
            for banco_nombre, cbu in BANCOS_DATA:
                banco_existente = BancoSociedad.query.filter_by(
                    sociedad_id=soc.id,
                    nombre_banco=banco_nombre
                ).first()
                if not banco_existente:
                    banco = BancoSociedad(
                        sociedad_id=soc.id,
                        nombre_banco=banco_nombre,
                        cbu=cbu,
                    )
                    db.session.add(banco)
            print(f"  [OK] {len(BANCOS_DATA)} bancos asignados a {soc.nombre}")

        db.session.commit()

        # 5. Crear proveedores
        print("\n[5] Creando proveedores...")
        proveedores = []
        for nombre, cuit_original, alias in PROVEEDORES_DATA:
            prov = Proveedor.query.filter_by(
                empresa_id=empresa.id,
                cuit=cuit_original
            ).first()
            if not prov:
                prov = Proveedor(
                    empresa_id=empresa.id,
                    cuit=cuit_original,
                    nombre=nombre,
                    cbu_alias=alias,
                )
                db.session.add(prov)
                proveedores.append(prov)

        # Agregar algunos proveedores más generados
        for i in range(5):
            nombre = f"Proveedor Adicional {i+1} S.A."
            cuit = generar_cuit_falso()
            alias = generar_alias_falso()

            prov = Proveedor.query.filter_by(
                empresa_id=empresa.id,
                cuit=cuit
            ).first()
            if not prov:
                prov = Proveedor(
                    empresa_id=empresa.id,
                    cuit=cuit,
                    nombre=nombre,
                    cbu_alias=alias,
                )
                db.session.add(prov)
                proveedores.append(prov)

        db.session.commit()
        print(f"[OK] {len(proveedores)} proveedores creados")

        # 6. Crear facturas/pagos (al menos 20)
        print("\n[6] Creando facturas y pagos...")
        facturas = []
        hoy = date.today()

        for i in range(25):
            sociedad = random.choice(sociedades)
            proveedor = random.choice(proveedores)
            banco = random.choice([b for b in BancoSociedad.query.all() if b.sociedad_id == sociedad.id])

            monto = round(random.uniform(500, 50000), 2)
            dias_offset = random.randint(-30, 60)
            fecha_prog = hoy + timedelta(days=dias_offset)
            fecha_venc = fecha_prog - timedelta(days=random.randint(5, 20))

            nro_factura = generar_nro_factura()
            estado = "pagado" if dias_offset < -5 else "pendiente"

            factura = FacturaPago(
                empresa_id=empresa.id,
                sociedad_id=sociedad.id,
                proveedor_id=proveedor.id,
                banco_origen_id=banco.id,
                nro_factura=nro_factura,
                nro_oc_op=f"OC-{random.randint(1000, 9999)}",
                monto=monto,
                fecha_vencimiento=fecha_venc,
                fecha_pago_programada=fecha_prog,
                tipo_gasto=random.choice(TIPOS_GASTOS),
                forma_pago=random.choice(FORMAS_PAGO),
                numero_cheque=f"{random.randint(100000, 999999)}" if random.random() > 0.7 else None,
                descripcion=f"Pago por servicios y materiales - Demo {i+1}",
                estado=estado,
            )
            db.session.add(factura)
            facturas.append(factura)

        db.session.commit()
        print(f"[OK] {len(facturas)} facturas creadas")

        # 7. Crear movimientos bancarios para conciliación
        print("\n[7] Creando movimientos bancarios...")
        movimientos = []

        for factura in facturas[:15]:  # Generar movimientos para algunas facturas
            if factura.estado == "pagado":
                descripcion = f"Pago a {Proveedor.query.get(factura.proveedor_id).nombre}"
                hash_dedup = generar_hash_dedup(
                    factura.fecha_pago_programada,
                    factura.monto,
                    descripcion
                )

                movimiento = MovimientoBancario(
                    empresa_id=empresa.id,
                    fecha=factura.fecha_pago_programada,
                    monto=factura.monto,
                    tipo="debito",
                    descripcion=descripcion,
                    hash_dedup=hash_dedup,
                    estado="conciliado",
                    factura_pago_id=factura.id,
                    categoria="pago",
                    conciliado_manual=False,
                )
                db.session.add(movimiento)
                movimientos.append(movimiento)

        # Agregar algunos movimientos sin conciliar
        for i in range(5):
            fecha = hoy - timedelta(days=random.randint(1, 10))
            monto = round(random.uniform(100, 5000), 2)
            descripcion = f"Movimiento demo sin conciliar {i+1}"
            hash_dedup = generar_hash_dedup(fecha, monto, descripcion)

            movimiento = MovimientoBancario(
                empresa_id=empresa.id,
                fecha=fecha,
                monto=monto,
                tipo="credito" if random.random() > 0.5 else "debito",
                descripcion=descripcion,
                hash_dedup=hash_dedup,
                estado="sin_conciliar",
                categoria="impuesto_gasto",
                conciliado_manual=False,
            )
            db.session.add(movimiento)
            movimientos.append(movimiento)

        db.session.commit()
        print(f"[OK] {len(movimientos)} movimientos bancarios creados")

        # 8. Crear recordatorios en agenda
        print("\n[8] Creando recordatorios...")
        recordatorios_data = [
            ("Revisar conciliacion bancaria", hoy + timedelta(days=3)),
            ("Pagar facturas del periodo anterior", hoy + timedelta(days=1)),
            ("Auditoria interna de tesoreria", hoy + timedelta(days=7)),
            ("Reunion con contador", hoy + timedelta(days=5)),
            ("Cierre de mes contable", hoy + timedelta(days=10)),
            ("Verificar disponibilidad de fondos", hoy),
            ("Preparar reporte de flujo de caja", hoy + timedelta(days=2)),
            ("Validar pagos en proceso", hoy + timedelta(days=1)),
            ("Contactar proveedores morosos", hoy + timedelta(days=4)),
            ("Arqueo de caja", hoy + timedelta(days=6)),
        ]

        recordatorios = []
        usuario_admin = usuarios[0] if usuarios else None

        if usuario_admin:
            for nota, fecha in recordatorios_data:
                rec = Recordatorio(
                    empresa_id=empresa.id,
                    usuario_id=usuario_admin.id,
                    fecha=fecha,
                    nota=nota,
                    hecho=False,
                    recurrencia="unica",
                )
                db.session.add(rec)
                recordatorios.append(rec)

            db.session.commit()
            print(f"[OK] {len(recordatorios)} recordatorios creados")

        # Mostrar resumen
        print("\n" + "="*60)
        print("SEED DE DEMO COMPLETADO EXITOSAMENTE")
        print("="*60)
        print(f"""
RESUMEN DE DATOS CARGADOS:

Empresa: {empresa.nombre}
   CUIT: {empresa.cuit}

Sociedades: {len(sociedades)}
   {chr(10).join([f"   - {s.nombre}" for s in sociedades])}

Empleados: {len(usuarios)}
   {chr(10).join([f"   - {u.nombre} ({u.rol})" for u in usuarios])}

Proveedores: {len(proveedores)}

Facturas/Pagos: {len(facturas)}
   - Pagadas: {sum(1 for f in facturas if f.estado == 'pagado')}
   - Pendientes: {sum(1 for f in facturas if f.estado == 'pendiente')}

Movimientos Bancarios: {len(movimientos)}
   - Conciliados: {sum(1 for m in movimientos if m.estado == 'conciliado')}
   - Sin Conciliar: {sum(1 for m in movimientos if m.estado == 'sin_conciliar')}

Recordatorios: {len(recordatorios)}

CREDENCIALES DE ACCESO (administrador):
   Email: {usuarios[0].email if usuarios else 'N/A'}
   Contraseña: Demo1234

IMPORTANTE: Reemplaza estos datos antes de usar en produccion.
""")
        print("="*60)

if __name__ == "__main__":
    seed_database()
