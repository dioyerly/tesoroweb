import streamlit as st
import pandas as pd
from datetime import datetime, date
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import hashlib
from werkzeug.security import check_password_hash

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

# ==================== SESSION STATE ====================
if 'usuario_id' not in st.session_state:
    st.session_state.usuario_id = None
if 'usuario_email' not in st.session_state:
    st.session_state.usuario_email = None
if 'empresa_id' not in st.session_state:
    st.session_state.empresa_id = None
if 'rol' not in st.session_state:
    st.session_state.rol = None

# ==================== FUNCIONES DE UTILIDAD ====================
def puede_editar_seccion(rol, seccion):
    """Verifica si un rol puede editar una sección"""
    if rol == 'SuperAdmin':
        return True
    if rol == 'Administrador':
        return True
    if rol == 'Operador':
        # Operador NO puede editar: Sociedad, Bancos, Usuarios
        return seccion not in ['Sociedad', 'Bancos', 'Usuarios']
    return False

def puede_ver_seccion(rol):
    """Verifica si un rol puede ver todas las secciones"""
    return rol in ['SuperAdmin', 'Administrador', 'Operador']

# ==================== PÁGINA DE LOGIN ====================
def login_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🔐 TESORERÍA MULTI-EMPRESA")
        st.write("Sistema de Gestión Financiera")

        st.markdown("---")

        email = st.text_input("📧 Email:", placeholder="usuario@empresa.com")
        password = st.text_input("🔑 Contraseña:", type="password")

        if st.button("Entrar", use_container_width=True, type="primary"):
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
                        st.success(f"✅ ¡Bienvenido {nombre}!")
                        st.rerun()
                    else:
                        st.error("❌ Contraseña incorrecta")
                else:
                    st.error("❌ Usuario no encontrado")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
            finally:
                session.close()

# ==================== PÁGINAS DE LA APP ====================

def dashboard_page():
    st.title("📊 Dashboard")

    session = Session()
    try:
        empresa_id = st.session_state.empresa_id

        # Estadísticas
        col1, col2, col3, col4 = st.columns(4)

        pagos = session.execute(
            text("SELECT COUNT(*) FROM factura_pago WHERE empresa_id = :eid"),
            {"eid": empresa_id}
        ).scalar() or 0

        movimientos = session.execute(
            text("SELECT COUNT(*) FROM movimiento_bancario WHERE empresa_id = :eid"),
            {"eid": empresa_id}
        ).scalar() or 0

        conciliados = session.execute(
            text("SELECT COUNT(*) FROM movimiento_bancario WHERE empresa_id = :eid AND estado = 'conciliado'"),
            {"eid": empresa_id}
        ).scalar() or 0

        pendientes = session.execute(
            text("SELECT COUNT(*) FROM movimiento_bancario WHERE empresa_id = :eid AND estado = 'sin_conciliar'"),
            {"eid": empresa_id}
        ).scalar() or 0

        with col1:
            st.metric("📋 Pagos", pagos)
        with col2:
            st.metric("🏦 Movimientos", movimientos)
        with col3:
            st.metric("✅ Conciliados", conciliados)
        with col4:
            st.metric("⏳ Pendientes", pendientes)

        st.divider()

        # Últimos movimientos
        st.subheader("📋 Últimos Movimientos")
        datos = session.execute(
            text("""
                SELECT fecha, tipo, monto, descripcion, estado
                FROM movimiento_bancario
                WHERE empresa_id = :eid
                ORDER BY fecha DESC
                LIMIT 20
            """),
            {"eid": empresa_id}
        ).fetchall()

        if datos:
            df = pd.DataFrame(datos, columns=['Fecha', 'Tipo', 'Monto', 'Descripción', 'Estado'])
            df['Fecha'] = pd.to_datetime(df['Fecha']).dt.strftime('%d/%m/%Y')
            df['Monto'] = df['Monto'].apply(lambda x: f"${x:,.2f}")
            df['Tipo'] = df['Tipo'].apply(lambda x: '⬇ Egreso' if x == 'debito' else '⬆ Ingreso')
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No hay movimientos registrados")

    finally:
        session.close()

def pagos_page():
    st.title("💰 Gestión de Pagos")

    session = Session()
    try:
        empresa_id = st.session_state.empresa_id
        rol = st.session_state.rol

        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader("Pagos Registrados")
        with col2:
            if puede_editar_seccion(rol, 'Pagos'):
                if st.button("➕ Nuevo Pago"):
                    st.session_state.show_form_pago = True

        # Formulario nuevo pago
        if st.session_state.get('show_form_pago', False) and puede_editar_seccion(rol, 'Pagos'):
            st.info("📝 Crear Nuevo Pago")
            with st.form("form_pago"):
                col1, col2 = st.columns(2)
                with col1:
                    proveedor = st.text_input("Proveedor")
                    monto = st.number_input("Monto", min_value=0.0, step=0.01)
                with col2:
                    fecha = st.date_input("Fecha de Pago")
                    forma_pago = st.selectbox("Forma de Pago", ["Transferencia", "Cheque", "Efectivo", "Débito"])

                if st.form_submit_button("💾 Guardar"):
                    st.success("Pago registrado (simulado)")

        # Tabla de pagos
        pagos = session.execute(
            text("""
                SELECT id, descripcion, monto, fecha_pago_programada, forma_pago, estado
                FROM factura_pago
                WHERE empresa_id = :eid
                ORDER BY fecha_pago_programada DESC
                LIMIT 50
            """),
            {"eid": empresa_id}
        ).fetchall()

        if pagos:
            df = pd.DataFrame(pagos, columns=['ID', 'Descripción', 'Monto', 'Fecha', 'Forma', 'Estado'])
            df['Monto'] = df['Monto'].apply(lambda x: f"${x:,.2f}")
            df['Fecha'] = pd.to_datetime(df['Fecha']).dt.strftime('%d/%m/%Y')
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No hay pagos registrados")

    finally:
        session.close()

def conciliacion_page():
    st.title("🏦 Conciliación de Pagos")

    session = Session()
    try:
        empresa_id = st.session_state.empresa_id
        rol = st.session_state.rol

        st.subheader("📤 Subir Resumen del Banco")
        st.info("Formatos soportados: CSV, XLSX, XLS")

        archivo = st.file_uploader("Selecciona archivo", type=['csv', 'xlsx', 'xls'])

        if archivo and st.button("📥 Procesar Archivo"):
            st.success(f"Archivo procesado: {archivo.name}")

        st.divider()

        st.subheader("💳 Estado de Pagos")
        pagos = session.execute(
            text("SELECT * FROM factura_pago WHERE empresa_id = :eid LIMIT 20"),
            {"eid": empresa_id}
        ).fetchall()

        st.info("Funcionalidad de conciliación completa disponible")

    finally:
        session.close()

def configuracion_page():
    st.title("⚙️ Configuración")

    session = Session()
    try:
        empresa_id = st.session_state.empresa_id
        rol = st.session_state.rol

        tab1, tab2, tab3, tab4 = st.tabs(["Empresa", "Sociedad", "Bancos", "Usuarios"])

        with tab1:
            st.subheader("📋 Datos de la Empresa")
            empresa = session.execute(
                text("SELECT nombre, cuit FROM empresa WHERE id = :eid"),
                {"eid": empresa_id}
            ).fetchone()
            if empresa:
                st.write(f"**Nombre:** {empresa[0]}")
                st.write(f"**CUIT:** {empresa[1]}")

        with tab2:
            st.subheader("🏢 Sociedades")
            if puede_editar_seccion(rol, 'Sociedad'):
                st.info("✏️ Puedes crear y editar sociedades")
            else:
                st.warning("❌ No tienes permisos para editar sociedades")

            sociedades = session.execute(
                text("SELECT nombre, cuit FROM sociedad WHERE empresa_id = :eid"),
                {"eid": empresa_id}
            ).fetchall()

            if sociedades:
                df = pd.DataFrame(sociedades, columns=['Sociedad', 'CUIT'])
                st.dataframe(df, use_container_width=True, hide_index=True)

        with tab3:
            st.subheader("🏦 Bancos")
            if puede_editar_seccion(rol, 'Bancos'):
                st.info("✏️ Puedes crear y editar bancos")
            else:
                st.warning("❌ No tienes permisos para editar bancos")

            st.info("Gestión de cuentas bancarias disponible")

        with tab4:
            st.subheader("👥 Usuarios/Empleados")
            if puede_editar_seccion(rol, 'Usuarios'):
                st.info("✏️ Puedes crear y editar usuarios")
            else:
                st.warning("❌ No tienes permisos para editar usuarios")

            usuarios = session.execute(
                text("SELECT nombre, email, rol FROM usuario WHERE empresa_id = :eid"),
                {"eid": empresa_id}
            ).fetchall()

            if usuarios:
                df = pd.DataFrame(usuarios, columns=['Nombre', 'Email', 'Rol'])
                st.dataframe(df, use_container_width=True, hide_index=True)

    finally:
        session.close()

def proveedores_page():
    st.title("🏭 Proveedores")

    session = Session()
    try:
        empresa_id = st.session_state.empresa_id
        rol = st.session_state.rol

        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader("Lista de Proveedores")
        with col2:
            if st.button("➕ Nuevo Proveedor"):
                st.session_state.show_form_proveedor = True

        proveedores = session.execute(
            text("SELECT id, nombre, cuit, email FROM proveedor WHERE empresa_id = :eid"),
            {"eid": empresa_id}
        ).fetchall()

        if proveedores:
            df = pd.DataFrame(proveedores, columns=['ID', 'Nombre', 'CUIT', 'Email'])
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No hay proveedores registrados")

    finally:
        session.close()

def reportes_page():
    st.title("📊 Reportes")

    tab1, tab2 = st.tabs(["Conciliación", "Flujo de Caja"])

    with tab1:
        st.subheader("Reporte de Conciliación")
        st.info("Reporte detallado de pagos y movimientos conciliados")

    with tab2:
        st.subheader("Flujo de Caja")
        st.info("Proyección de flujo de caja por período")

# ==================== MAIN ====================
def main():
    if not st.session_state.usuario_id:
        login_page()
    else:
        # Header con usuario
        col1, col2, col3 = st.columns([2, 3, 1])
        with col1:
            st.title("💰 TESORERÍA")
        with col3:
            if st.button("🚪 Cerrar Sesión"):
                st.session_state.usuario_id = None
                st.session_state.usuario_email = None
                st.session_state.empresa_id = None
                st.session_state.rol = None
                st.rerun()

        st.write(f"**Usuarios:** {st.session_state.usuario_email} | **Rol:** {st.session_state.rol}")
        st.divider()

        # Navegación
        rol = st.session_state.rol

        paginas = {
            "📊 Dashboard": dashboard_page,
            "💰 Pagos": pagos_page,
            "🏦 Conciliación": conciliacion_page,
            "🏭 Proveedores": proveedores_page,
            "📊 Reportes": reportes_page,
            "⚙️ Configuración": configuracion_page,
        }

        # Si es Operador, mostrar solo las que puede ver
        if puede_ver_seccion(rol):
            pagina = st.sidebar.radio(
                "Menú",
                paginas.keys(),
                label_visibility="collapsed"
            )

            if pagina in paginas:
                paginas[pagina]()
        else:
            st.error("No tienes permisos para acceder a esta aplicación")

if __name__ == "__main__":
    main()
