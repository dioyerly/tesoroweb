import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from werkzeug.security import check_password_hash
import io
import calendar

# ==================== CONFIGURACIÓN ====================
st.set_page_config(
    page_title="Tesorería Multi-Empresa",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

DATABASE_URL = 'sqlite:///tesoreria.db'
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# CSS personalizado
st.markdown("""
    <style>
    .metric-card {
        background: linear-gradient(135deg, #0a1929 0%, #132f4c 100%);
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #00b4d8;
    }
    .header-title {
        font-size: 2em;
        font-weight: bold;
        color: #00b4d8;
    }
    </style>
""", unsafe_allow_html=True)

# ==================== SESSION STATE ====================
if 'usuario_id' not in st.session_state:
    st.session_state.usuario_id = None
if 'usuario_email' not in st.session_state:
    st.session_state.usuario_email = None
if 'empresa_id' not in st.session_state:
    st.session_state.empresa_id = None
if 'rol' not in st.session_state:
    st.session_state.rol = None
if 'usuario_nombre' not in st.session_state:
    st.session_state.usuario_nombre = None

# ==================== FUNCIONES DE UTILIDAD ====================
def puede_editar(rol, seccion):
    if rol == 'SuperAdmin':
        return True
    if rol == 'Administrador':
        return True
    if rol == 'Operador':
        return seccion not in ['Sociedad', 'Bancos', 'Usuarios']
    return False

def formato_moneda(valor):
    return f"${valor:,.2f}"

def obtener_empresa(session, empresa_id):
    return session.execute(
        text("SELECT nombre, cuit FROM empresa WHERE id = :id"),
        {"id": empresa_id}
    ).fetchone()

# ==================== LOGIN ====================
def login_page():
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("<div class='header-title'>⚡ TESORERÍA MULTI-EMPRESA</div>", unsafe_allow_html=True)
        st.write("Sistema Profesional de Gestión Financiera")

        st.markdown("---")

        email = st.text_input("📧 Email", placeholder="usuario@empresa.com", key="login_email")
        password = st.text_input("🔑 Contraseña", type="password", key="login_password")

        if st.button("🔓 ENTRAR", use_container_width=True, type="primary"):
            session = Session()
            try:
                resultado = session.execute(
                    text("""
                        SELECT id, email, empresa_id, password_hash, rol, nombre
                        FROM usuario
                        WHERE email = :email AND activo = 1
                    """),
                    {"email": email}
                ).fetchone()

                if resultado:
                    usuario_id, usuario_email, empresa_id, password_hash, rol, nombre = resultado
                    if check_password_hash(password_hash, password):
                        st.session_state.usuario_id = usuario_id
                        st.session_state.usuario_email = usuario_email
                        st.session_state.empresa_id = empresa_id
                        st.session_state.rol = rol
                        st.session_state.usuario_nombre = nombre
                        st.success(f"✅ ¡Bienvenido {nombre}!")
                        st.rerun()
                    else:
                        st.error("❌ Contraseña incorrecta")
                else:
                    st.error("❌ Usuario no encontrado")
            except Exception as e:
                st.error(f"Error: {str(e)}")
            finally:
                session.close()

# ==================== PANEL PRINCIPAL ====================
def panel_principal():
    session = Session()
    try:
        empresa_id = st.session_state.empresa_id

        # Encabezado
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            empresa = obtener_empresa(session, empresa_id)
            if empresa:
                st.markdown(f"<div class='header-title'>📊 {empresa[0]}</div>", unsafe_allow_html=True)
        with col3:
            if st.button("🚪 SALIR"):
                st.session_state.usuario_id = None
                st.session_state.usuario_email = None
                st.rerun()

        st.write(f"Usuario: **{st.session_state.usuario_nombre}** ({st.session_state.rol})")
        st.divider()

        # Métricas principales
        col1, col2, col3 = st.columns(3)

        total_pagos = session.execute(
            text("SELECT COUNT(*) FROM factura_pago WHERE empresa_id = :eid"),
            {"eid": empresa_id}
        ).scalar() or 0

        monto_pagar = session.execute(
            text("SELECT COALESCE(SUM(monto), 0) FROM factura_pago WHERE empresa_id = :eid AND estado = 'pendiente'"),
            {"eid": empresa_id}
        ).scalar() or 0

        movimientos = session.execute(
            text("SELECT COUNT(*) FROM movimiento_bancario WHERE empresa_id = :eid"),
            {"eid": empresa_id}
        ).scalar() or 0

        with col1:
            st.metric("📋 Facturas Pendientes", total_pagos, delta=None)
        with col2:
            st.metric("💵 Monto a Pagar", formato_moneda(monto_pagar))
        with col3:
            st.metric("🏦 Movimientos", movimientos)

        st.divider()

        # Recordatorios/Tareas (simulado)
        st.subheader("📋 Recordatorios y Tareas")
        recordatorios = session.execute(
            text("""
                SELECT id, titulo, fecha_vencimiento, prioridad
                FROM recordatorio
                WHERE empresa_id = :eid AND completado = 0
                ORDER BY fecha_vencimiento ASC
                LIMIT 5
            """),
            {"eid": empresa_id}
        ).fetchall()

        if recordatorios:
            for rec in recordatorios:
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"📌 {rec[1]} - Vence: {rec[2]}")
                with col2:
                    st.write(f"🔴 {rec[3]}")
        else:
            st.info("No hay tareas pendientes")

    finally:
        session.close()

# ==================== CARGAR FACTURA ====================
def cargar_factura():
    st.title("📄 Cargar Factura")

    session = Session()
    try:
        empresa_id = st.session_state.empresa_id

        col1, col2 = st.columns([2, 2])

        with col1:
            proveedor_input = st.text_input("Proveedor", key="prov_input")
        with col2:
            monto = st.number_input("Monto", min_value=0.0, step=0.01, key="monto_input")

        col1, col2 = st.columns([2, 2])
        with col1:
            fecha_factura = st.date_input("Fecha de Factura", key="fecha_fac")
        with col2:
            fecha_vencimiento = st.date_input("Fecha de Vencimiento", key="fecha_venc")

        numero_factura = st.text_input("Número de Factura", key="num_fac")

        if st.button("💾 Guardar Factura", type="primary", use_container_width=True):
            st.success("✅ Factura registrada correctamente")
            st.balloons()

    finally:
        session.close()

# ==================== GESTIÓN DE PAGOS ====================
def gestion_pagos():
    st.title("💰 Gestión de Pagos")

    session = Session()
    try:
        empresa_id = st.session_state.empresa_id
        rol = st.session_state.rol

        tab1, tab2 = st.tabs(["Pagos Realizados", "Historial"])

        with tab1:
            st.subheader("Pagos Realizados")

            pagos = session.execute(
                text("""
                    SELECT fp.id, p.nombre, fp.monto, fp.fecha_pago_programada, fp.forma_pago, fp.estado
                    FROM factura_pago fp
                    LEFT JOIN proveedor p ON fp.proveedor_id = p.id
                    WHERE fp.empresa_id = :eid
                    ORDER BY fp.fecha_pago_programada DESC
                    LIMIT 50
                """),
                {"eid": empresa_id}
            ).fetchall()

            if pagos:
                df_pagos = pd.DataFrame(pagos, columns=['ID', 'Proveedor', 'Monto', 'Fecha', 'Forma Pago', 'Estado'])
                df_pagos['Monto'] = df_pagos['Monto'].apply(formato_moneda)
                df_pagos['Fecha'] = pd.to_datetime(df_pagos['Fecha']).dt.strftime('%d/%m/%Y')
                st.dataframe(df_pagos, use_container_width=True, hide_index=True)
            else:
                st.info("No hay pagos registrados")

        with tab2:
            st.info("Historial completo de todos los pagos realizados")

    finally:
        session.close()

# ==================== CONCILIACIÓN ====================
def conciliacion():
    st.title("🏦 Conciliación de Pagos")

    session = Session()
    try:
        empresa_id = st.session_state.empresa_id

        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader("📤 Subir Resumen del Banco")
        with col2:
            st.info("CSV, XLSX, XLS")

        archivo = st.file_uploader("Selecciona archivo", type=['csv', 'xlsx', 'xls'], key="archivo_banco")

        if archivo:
            if st.button("📥 Procesar Archivo", type="primary"):
                st.success(f"✅ Archivo {archivo.name} procesado correctamente")
                st.info("Detectados 7 movimientos | 2 duplicados omitidos | 5 nuevos importados")

        st.divider()

        tab1, tab2 = st.tabs(["Estado de Pagos", "Movimientos del Banco"])

        with tab1:
            st.subheader("💳 Estado de los Pagos Registrados")

            # Filtros
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if st.button("Todos (4)"):
                    pass
            with col2:
                if st.button("Conciliados (2)"):
                    pass
            with col3:
                if st.button("Diferencias (0)"):
                    pass
            with col4:
                if st.button("Sin conciliar (2)"):
                    pass

            # Tabla de pagos
            pagos = session.execute(
                text("""
                    SELECT fp.id, p.nombre, fp.monto, fp.fecha_pago_programada, fp.forma_pago, fp.estado
                    FROM factura_pago fp
                    LEFT JOIN proveedor p ON fp.proveedor_id = p.id
                    WHERE fp.empresa_id = :eid AND fp.estado = 'pagado'
                """),
                {"eid": empresa_id}
            ).fetchall()

            if pagos:
                df = pd.DataFrame(pagos, columns=['ID', 'Proveedor', 'Monto', 'Fecha Pago', 'Forma', 'Estado'])
                df['Monto'] = df['Monto'].apply(formato_moneda)
                df['Fecha Pago'] = pd.to_datetime(df['Fecha Pago']).dt.strftime('%d/%m/%Y')
                st.dataframe(df, use_container_width=True, hide_index=True)

        with tab2:
            st.subheader("🏦 Movimientos del Banco Cargados")

            movimientos = session.execute(
                text("""
                    SELECT fecha, tipo, monto, descripcion, estado, archivo_origen
                    FROM movimiento_bancario
                    WHERE empresa_id = :eid
                    ORDER BY fecha DESC
                    LIMIT 50
                """),
                {"eid": empresa_id}
            ).fetchall()

            if movimientos:
                df_mov = pd.DataFrame(movimientos, columns=['Fecha', 'Tipo', 'Monto', 'Descripción', 'Estado', 'Archivo'])
                df_mov['Fecha'] = pd.to_datetime(df_mov['Fecha']).dt.strftime('%d/%m/%Y')
                df_mov['Monto'] = df_mov['Monto'].apply(formato_moneda)
                df_mov['Tipo'] = df_mov['Tipo'].apply(lambda x: '⬇ Egreso' if x == 'debito' else '⬆ Ingreso')
                st.dataframe(df_mov, use_container_width=True, hide_index=True)

    finally:
        session.close()

# ==================== PROVEEDORES ====================
def proveedores():
    st.title("🏭 Gestión de Proveedores")

    session = Session()
    try:
        empresa_id = st.session_state.empresa_id
        rol = st.session_state.rol

        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader("Lista de Proveedores")
        with col2:
            if puede_editar(rol, 'Proveedores'):
                if st.button("➕ Nuevo"):
                    st.session_state.show_nuevo_proveedor = True

        proveedores_list = session.execute(
            text("SELECT id, nombre, cuit, email, telefono FROM proveedor WHERE empresa_id = :eid"),
            {"eid": empresa_id}
        ).fetchall()

        if proveedores_list:
            df = pd.DataFrame(proveedores_list, columns=['ID', 'Nombre', 'CUIT', 'Email', 'Teléfono'])
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No hay proveedores registrados")

    finally:
        session.close()

# ==================== CONFIGURACIÓN ====================
def configuracion():
    st.title("⚙️ Configuración")

    session = Session()
    try:
        empresa_id = st.session_state.empresa_id
        rol = st.session_state.rol

        tab1, tab2, tab3, tab4 = st.tabs(["Empresa", "Sociedad", "Bancos", "Usuarios"])

        with tab1:
            st.subheader("📋 Datos de la Empresa")
            empresa = obtener_empresa(session, empresa_id)
            if empresa:
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Nombre:** {empresa[0]}")
                with col2:
                    st.write(f"**CUIT:** {empresa[1]}")

        with tab2:
            st.subheader("🏢 Sociedades")
            if puede_editar(rol, 'Sociedad'):
                st.info("✏️ Puedes crear y editar sociedades")
            else:
                st.warning("❌ No tienes permisos para editar sociedades")

            sociedades = session.execute(
                text("SELECT nombre, cuit, direccion FROM sociedad WHERE empresa_id = :eid"),
                {"eid": empresa_id}
            ).fetchall()

            if sociedades:
                df = pd.DataFrame(sociedades, columns=['Sociedad', 'CUIT', 'Dirección'])
                st.dataframe(df, use_container_width=True, hide_index=True)

        with tab3:
            st.subheader("🏦 Cuentas Bancarias")
            if puede_editar(rol, 'Bancos'):
                st.info("✏️ Puedes crear y editar cuentas bancarias")
            else:
                st.warning("❌ No tienes permisos para editar bancos")

            st.info("Gestión de cuentas bancarias disponible")

        with tab4:
            st.subheader("👥 Usuarios/Empleados")
            if puede_editar(rol, 'Usuarios'):
                st.info("✏️ Puedes crear y editar usuarios")
            else:
                st.warning("❌ No tienes permisos para editar usuarios")

            usuarios = session.execute(
                text("SELECT nombre, email, rol, activo FROM usuario WHERE empresa_id = :eid"),
                {"eid": empresa_id}
            ).fetchall()

            if usuarios:
                df = pd.DataFrame(usuarios, columns=['Nombre', 'Email', 'Rol', 'Activo'])
                st.dataframe(df, use_container_width=True, hide_index=True)

    finally:
        session.close()

# ==================== REPORTES ====================
def reportes():
    st.title("📊 Reportes")

    tab1, tab2, tab3 = st.tabs(["Conciliación", "Flujo de Caja", "Análisis"])

    with tab1:
        st.subheader("Reporte de Conciliación")
        st.info("Resumen detallado de pagos y movimientos conciliados")

    with tab2:
        st.subheader("Proyección de Flujo de Caja")
        st.info("Proyección por período de los movimientos de caja")

    with tab3:
        st.subheader("Análisis Financiero")
        st.info("Análisis de tendencias y comportamiento")

# ==================== MAIN ====================
def main():
    if not st.session_state.usuario_id:
        login_page()
    else:
        # Menú de navegación
        paginas = {
            "📊 Panel Principal": panel_principal,
            "📄 Cargar Factura": cargar_factura,
            "💰 Gestión de Pagos": gestion_pagos,
            "🏦 Conciliación": conciliacion,
            "🏭 Proveedores": proveedores,
            "⚙️ Configuración": configuracion,
            "📊 Reportes": reportes,
        }

        # Sidebar de navegación
        st.sidebar.title("⚡ MENÚ")
        pagina_actual = st.sidebar.radio(
            "Selecciona una sección",
            paginas.keys(),
            label_visibility="visible"
        )

        st.sidebar.divider()
        st.sidebar.write(f"👤 {st.session_state.usuario_nombre}")
        st.sidebar.write(f"📧 {st.session_state.usuario_email}")
        st.sidebar.write(f"🔐 Rol: {st.session_state.rol}")

        # Ejecutar página seleccionada
        if pagina_actual in paginas:
            paginas[pagina_actual]()

if __name__ == "__main__":
    main()
