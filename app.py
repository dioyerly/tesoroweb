import streamlit as st
import pandas as pd
from datetime import datetime, date
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys

# Agregar el directorio actual al path para imports
sys.path.insert(0, os.path.dirname(__file__))

from models import db, Usuario, Empresa, Proveedor, FacturaPago, MovimientoBancario, MovimientoSplit
from app_flask import (
    _leer_movimientos_banco,
    _construir_vista_conciliacion,
    _limpiar_duplicados_movimientos,
    _reconciliar_todo,
    _normalizar_columna,
    _parsear_monto
)

# Configuración de la página
st.set_page_config(
    page_title="Tesorería - Conciliación Bancaria",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configurar conexión a BD
DATABASE_URL = 'sqlite:///tesoreria.db'
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# CSS personalizado
st.markdown("""
    <style>
    .main { padding: 2rem; }
    .metric-card { background: #f0f2f6; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; }
    </style>
""", unsafe_allow_html=True)

# ==================== AUTENTICACIÓN ====================
def init_session_state():
    if 'usuario_id' not in st.session_state:
        st.session_state.usuario_id = None
    if 'usuario_email' not in st.session_state:
        st.session_state.usuario_email = None
    if 'empresa_id' not in st.session_state:
        st.session_state.empresa_id = None

init_session_state()

def login_page():
    st.title("🔐 Iniciar Sesión")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        email = st.text_input("Email:", placeholder="tu@email.com")
        password = st.text_input("Contraseña:", type="password")

        if st.button("Entrar", use_container_width=True):
            session = Session()
            try:
                usuario = session.query(Usuario).filter_by(email=email, activo=True).first()
                if usuario and usuario.check_password(password):
                    st.session_state.usuario_id = usuario.id
                    st.session_state.usuario_email = usuario.email

                    # Obtener empresa del usuario
                    if usuario.empresa_id:
                        st.session_state.empresa_id = usuario.empresa_id

                    st.success("¡Bienvenido!")
                    st.rerun()
                else:
                    st.error("Email o contraseña incorrectos")
            finally:
                session.close()

# ==================== PÁGINAS PRINCIPALES ====================
def dashboard_page():
    st.title("📊 Dashboard")

    session = Session()
    try:
        empresa_id = st.session_state.empresa_id

        # Estadísticas
        col1, col2, col3, col4 = st.columns(4)

        pagos_totales = session.query(FacturaPago).filter_by(empresa_id=empresa_id).count()
        movimientos_totales = session.query(MovimientoBancario).filter_by(empresa_id=empresa_id).count()

        with col1:
            st.metric("Total Pagos", pagos_totales)
        with col2:
            st.metric("Total Movimientos", movimientos_totales)
        with col3:
            pagos_conciliados = session.query(FacturaPago).filter_by(
                empresa_id=empresa_id,
                estado='pagado'
            ).count()
            st.metric("Pagos Conciliados", pagos_conciliados)
        with col4:
            movimientos_sin_conc = session.query(MovimientoBancario).filter_by(
                empresa_id=empresa_id,
                estado='sin_conciliar'
            ).count()
            st.metric("Movimientos Pendientes", movimientos_sin_conc)

        st.divider()

        # Últimos movimientos
        st.subheader("📋 Últimos Movimientos")
        movimientos = session.query(MovimientoBancario).filter_by(
            empresa_id=empresa_id
        ).order_by(MovimientoBancario.fecha.desc()).limit(10).all()

        if movimientos:
            df_movimientos = pd.DataFrame([{
                'Fecha': m.fecha.strftime('%d/%m/%Y'),
                'Tipo': '⬇ Egreso' if m.tipo == 'debito' else '⬆ Ingreso',
                'Monto': f"${m.monto:,.2f}",
                'Descripción': m.descripcion[:50],
                'Estado': m.estado
            } for m in movimientos])

            st.dataframe(df_movimientos, use_container_width=True, hide_index=True)
        else:
            st.info("No hay movimientos registrados aún")

    finally:
        session.close()

def conciliacion_page():
    st.title("🏦 Conciliación de Pagos")

    session = Session()
    try:
        empresa_id = st.session_state.empresa_id

        # Subir archivo
        st.subheader("📤 Subir Resumen del Banco")
        archivo = st.file_uploader(
            "Selecciona archivo CSV o Excel",
            type=['csv', 'xlsx', 'xls'],
            key='archivo_banco'
        )

        if archivo:
            if st.button("Procesar Archivo"):
                try:
                    # Guardar archivo temporalmente
                    ruta_temp = f"/tmp/{archivo.name}"
                    with open(ruta_temp, 'wb') as f:
                        f.write(archivo.getbuffer())

                    # Leer movimientos
                    movimientos = _leer_movimientos_banco(ruta_temp)

                    # Insertar en BD
                    nuevos = 0
                    duplicados = 0

                    for m in movimientos:
                        # Verificar si ya existe
                        existe = session.query(MovimientoBancario).filter_by(
                            empresa_id=empresa_id,
                            hash_dedup=m['hash_dedup']
                        ).first()

                        if existe:
                            duplicados += 1
                        else:
                            mov = MovimientoBancario(
                                empresa_id=empresa_id,
                                fecha=m['fecha'],
                                monto=m['monto'],
                                tipo=m['tipo'],
                                descripcion=m['descripcion'],
                                hash_dedup=m['hash_dedup'],
                                estado='ingreso' if m['tipo'] == 'credito' else 'sin_conciliar',
                                categoria='ingreso' if m['tipo'] == 'credito' else 'otros',
                                archivo_origen=archivo.name
                            )
                            session.add(mov)
                            nuevos += 1

                    session.commit()

                    # Limpiar duplicados
                    eliminados_dup = _limpiar_duplicados_movimientos(empresa_id)

                    # Reconciliar
                    _reconciliar_todo(empresa_id)

                    st.success(f"""
                    ✅ Importación completada
                    - {nuevos} movimiento(s) nuevo(s)
                    - {duplicados} duplicado(s) omitido(s)
                    - {eliminados_dup} duplicado(s) eliminado(s)
                    """)
                    st.rerun()

                except Exception as e:
                    st.error(f"Error al procesar archivo: {str(e)}")

        st.divider()

        # Tabla de pagos
        st.subheader("💳 Estado de los Pagos Registrados")

        pagos = session.query(FacturaPago).filter_by(empresa_id=empresa_id, estado='pagado').all()

        if pagos:
            df_pagos = pd.DataFrame([{
                'Proveedor': pagos[0].proveedor.nombre if pagos[0].proveedor else pagos[0].descripcion,
                'Monto': f"${p.monto:,.2f}",
                'Fecha': p.fecha_pago_programada.strftime('%d/%m/%Y') if p.fecha_pago_programada else '-',
                'Forma de Pago': p.forma_pago or 'Transferencia',
                'Estado': '✅ Pagado'
            } for p in pagos])

            st.dataframe(df_pagos, use_container_width=True, hide_index=True)
        else:
            st.info("No hay pagos registrados")

        st.divider()

        # Tabla de movimientos
        st.subheader("🏦 Movimientos del Banco Cargados")

        movimientos = session.query(MovimientoBancario).filter_by(
            empresa_id=empresa_id
        ).order_by(MovimientoBancario.fecha.desc()).all()

        if movimientos:
            df_movimientos = pd.DataFrame([{
                'Fecha': m.fecha.strftime('%d/%m/%Y'),
                'Tipo': '⬇ Egreso' if m.tipo == 'debito' else '⬆ Ingreso',
                'Monto': f"${m.monto:,.2f}",
                'Descripción': m.descripcion[:60],
                'Estado': m.estado,
                'Archivo': m.archivo_origen
            } for m in movimientos])

            st.dataframe(df_movimientos, use_container_width=True, hide_index=True)
        else:
            st.info("No hay movimientos cargados aún")

    finally:
        session.close()

def pagos_page():
    st.title("💰 Gestión de Pagos")

    session = Session()
    try:
        empresa_id = st.session_state.empresa_id

        st.subheader("Pagos Registrados")

        pagos = session.query(FacturaPago).filter_by(empresa_id=empresa_id).all()

        if pagos:
            df_pagos = pd.DataFrame([{
                'ID': p.id,
                'Proveedor': p.proveedor.nombre if p.proveedor else p.descripcion,
                'Monto': f"${p.monto:,.2f}",
                'Fecha': p.fecha_pago_programada.strftime('%d/%m/%Y') if p.fecha_pago_programada else '-',
                'Estado': p.estado,
                'Forma de Pago': p.forma_pago or '-'
            } for p in pagos])

            st.dataframe(df_pagos, use_container_width=True, hide_index=True)
        else:
            st.info("No hay pagos registrados")

    finally:
        session.close()

# ==================== MAIN ====================
def main():
    if not st.session_state.usuario_id:
        login_page()
    else:
        # Sidebar con navegación
        with st.sidebar:
            st.title(f"👤 {st.session_state.usuario_email}")

            página = st.radio(
                "Navegación",
                ["📊 Dashboard", "🏦 Conciliación", "💰 Pagos"],
                label_visibility="collapsed"
            )

            st.divider()

            if st.button("🚪 Cerrar Sesión", use_container_width=True):
                st.session_state.usuario_id = None
                st.session_state.usuario_email = None
                st.session_state.empresa_id = None
                st.rerun()

        # Mostrar página seleccionada
        if página == "📊 Dashboard":
            dashboard_page()
        elif página == "🏦 Conciliación":
            conciliacion_page()
        elif página == "💰 Pagos":
            pagos_page()

if __name__ == "__main__":
    main()
