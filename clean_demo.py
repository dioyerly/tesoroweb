#!/usr/bin/env python3
"""
Script para limpiar y regenerar datos de demo
"""

from app import app, db
from models import (
    Empresa, Usuario, Sociedad, BancoSociedad, Proveedor,
    FacturaPago, Recordatorio, MovimientoBancario, Conciliacion
)

def clean_database():
    """Elimina todos los datos de demostración"""

    with app.app_context():
        print("[*] Limpiando base de datos de datos anteriores...")

        # Eliminar en orden inverso de dependencias
        print("[1] Eliminando movimientos bancarios...")
        MovimientoBancario.query.delete()

        print("[2] Eliminando conciliaciones...")
        Conciliacion.query.delete()

        print("[3] Eliminando recordatorios...")
        Recordatorio.query.delete()

        print("[4] Eliminando facturas...")
        FacturaPago.query.delete()

        print("[5] Eliminando proveedores...")
        Proveedor.query.delete()

        print("[6] Eliminando bancos...")
        BancoSociedad.query.delete()

        print("[7] Eliminando sociedades...")
        Sociedad.query.delete()

        print("[8] Eliminando usuarios (excepto SuperAdmin)...")
        Usuario.query.filter(Usuario.rol != 'SuperAdmin').delete()

        print("[9] Eliminando empresas demo (excepto SuperAdmin)...")
        # Eliminar empresas que no tengan usuarios SuperAdmin
        superadmin = Usuario.query.filter_by(rol='SuperAdmin').first()
        if superadmin:
            # Eliminar todas las empresas excepto la del SuperAdmin
            Empresa.query.filter(Empresa.id != superadmin.empresa_id).delete()

        db.session.commit()

        print("\n[OK] Base de datos limpiada exitosamente")

if __name__ == "__main__":
    clean_database()
