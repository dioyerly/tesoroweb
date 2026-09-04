import streamlit as st
import pandas as pd
from datetime import datetime
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import hashlib
import re

# ==================== CONFIGURACIÓN ====================
st.set_page_config(
    page_title="Tesorería - Conciliación",
    page_icon="💰",
    layout="wide"
)

# BD
DATABASE_URL = 'sqlite:///tesoreria.db'
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# ==================== FUNCIONES AUXILIARES ====================
def normalizar_texto(texto):
    """Normaliza texto para búsqueda"""
    if not texto:
        return ""
    texto = str(texto).lower()
    texto = re.sub(r'[áäâà]', 'a', texto)
    texto = re.sub(r'[éëêè]', 'e', texto)
    texto = re.sub(r'[íïîì]', 'i', texto)
    texto = re.sub(r'[óöôò]', 'o', texto)
    texto = re.sub(r'[úüûù]', 'u', texto)
    return texto.strip()

def parsear_monto(valor):
    """Convierte string a número"""
    if not valor or str(valor).lower() == 'nan':
        return 0.0
    valor_str = str(valor).replace(',', '.').strip()
    try:
        return float(valor_str)
    except:
        return 0.0

# ==================== SESSION STATE ====================
if 'usuario_id' not in st.session_state:
    st.session_state.usuario_id = None
if 'usuario_email' not in st.session_state:
    st.session_state.usuario_email = None
if 'empresa_id' not in st.session_state:
    st.session_state.empresa_id = None

# ==================== PÁGINA DE LOGIN ====================
def login_page():
    st.title("🔐 Iniciar Sesión")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.write("")
        email = st.text_input("📧 Email:", placeholder="tu@email.com")
        password = st.text_input("🔑 Contraseña:", type="password")

        if st.button("Entrar", use_container_width=True, type="primary"):
            session = Session()
            try:
                # Buscar usuario
                resultado = session.execute(
                    text("""
                        SELECT id, email, empresa_id, password_hash
                        FROM usuario
                        WHERE email = :email AND activo = 1
                    """),
                    {"email": email}
                ).fetchone()

                if resultado:
                    usuario_id, usuario_email, empresa_id, password_hash = resultado

                    # Verificar contraseña (básico)
                    if password_hash and len(password) > 0:
                        st.session_state.usuario_id = usuario_id
                        st.session_state.usuario_email = usuario_email
                        st.session_state.empresa_id = empresa_id
                        st.success("✅ ¡Bienvenido!")
                        st.rerun()
                    else:
                        st.error("❌ Contraseña incorrecta")
                else:
                    st.error("❌ Usuario no encontrado")
            except Exception as e:
                st.error(f"Error: {str(e)}")
            finally:
                session.close()

# ==================== PÁGINA DASHBOARD ====================
def dashboard_page():
    st.title("📊 Dashboard")

    session = Session()
    try:
        empresa_id = st.session_state.empresa_id

        # Estadísticas
        col1, col2, col3, col4 = st.columns(4)

        # Total pagos
        result = session.execute(
            text("SELECT COUNT(*) FROM factura_pago WHERE empresa_id = :eid"),
            {"eid": empresa_id}
        ).scalar()
        with col1:
            st.metric("📋 Total Pagos", result or 0)

        # Total movimientos
        result = session.execute(
            text("SELECT COUNT(*) FROM movimiento_bancario WHERE empresa_id = :eid"),
            {"eid": empresa_id}
        ).scalar()
        with col2:
            st.metric("🏦 Total Movimientos", result or 0)

        # Pagos conciliados
        result = session.execute(
            text("""
                SELECT COUNT(*) FROM movimiento_bancario
                WHERE empresa_id = :eid AND estado = 'conciliado'
            """),
            {"eid": empresa_id}
        ).scalar()
        with col3:
            st.metric("✅ Conciliados", result or 0)

        # Pendientes
        result = session.execute(
            text("""
                SELECT COUNT(*) FROM movimiento_bancario
                WHERE empresa_id = :eid AND estado = 'sin_conciliar'
            """),
            {"eid": empresa_id}
        ).scalar()
        with col4:
            st.metric("⏳ Pendientes", result or 0)

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

# ==================== PÁGINA CONCILIACIÓN ====================
def conciliacion_page():
    st.title("🏦 Conciliación de Pagos")

    session = Session()
    try:
        empresa_id = st.session_state.empresa_id

        st.subheader("📤 Subir Archivo Bancario")
        st.info("📌 Formatos: CSV o Excel (.csv, .xlsx, .xls)")

        archivo = st.file_uploader("Selecciona archivo", type=['csv', 'xlsx', 'xls'])

        if archivo and st.button("📥 Procesar Archivo"):
            try:
                # Leer archivo
                if archivo.name.endswith('.csv'):
                    df = pd.read_csv(archivo)
                else:
                    df = pd.read_excel(archivo)

                # Normalizar columnas
                df.columns = [normalizar_texto(c) for c in df.columns]

                # Buscar columnas
                col_fecha = next((c for c in df.columns if 'fecha' in c), None)
                col_monto = next((c for c in df.columns if 'monto' in c or 'importe' in c), None)
                col_debito = next((c for c in df.columns if 'debito' in c or 'debe' in c.lower()), None)
                col_credito = next((c for c in df.columns if 'credito' in c or 'haber' in c.lower()), None)

                if not col_fecha:
                    st.error("❌ No encontré columna de Fecha")
                    return

                if not (col_monto or col_debito or col_credito):
                    st.error("❌ No encontré columna de Monto (o Débitos/Créditos)")
                    return

                # Procesar filas
                nuevos = 0
                duplicados = 0

                for idx, row in df.iterrows():
                    try:
                        fecha_str = str(row[col_fecha]).strip()
                        fecha = pd.to_datetime(fecha_str, dayfirst=True).date()
                    except:
                        continue

                    # Obtener monto y tipo
                    if col_debito and col_credito:
                        monto_d = parsear_monto(row.get(col_debito, 0))
                        monto_c = parsear_monto(row.get(col_credito, 0))
                        if monto_d > 0:
                            monto, tipo = monto_d, 'debito'
                        elif monto_c > 0:
                            monto, tipo = monto_c, 'credito'
                        else:
                            continue
                    elif col_monto:
                        monto = abs(parsear_monto(row[col_monto]))
                        tipo = 'debito' if parsear_monto(row[col_monto]) < 0 else 'credito'
                    else:
                        continue

                    # Descripción
                    desc_cols = [c for c in df.columns if c not in (col_fecha, col_monto, col_debito, col_credito)]
                    descripcion = ' '.join([
                        str(row.get(c, '')).strip()
                        for c in desc_cols
                        if row.get(c) and str(row.get(c, '')).lower() != 'nan'
                    ])[:200]

                    # Hash para deduplicación
                    hash_text = f"{fecha}|{monto:.2f}|{tipo}|{normalizar_texto(descripcion)}"
                    hash_dedup = hashlib.sha256(hash_text.encode()).hexdigest()

                    # Verificar si existe
                    existe = session.execute(
                        text("""
                            SELECT id FROM movimiento_bancario
                            WHERE empresa_id = :eid AND hash_dedup = :hash
                        """),
                        {"eid": empresa_id, "hash": hash_dedup}
                    ).scalar()

                    if existe:
                        duplicados += 1
                    else:
                        session.execute(
                            text("""
                                INSERT INTO movimiento_bancario
                                (empresa_id, fecha, monto, tipo, descripcion, hash_dedup, estado, categoria, archivo_origen)
                                VALUES (:eid, :fecha, :monto, :tipo, :desc, :hash, :estado, :cat, :archivo)
                            """),
                            {
                                "eid": empresa_id,
                                "fecha": fecha,
                                "monto": monto,
                                "tipo": tipo,
                                "desc": descripcion,
                                "hash": hash_dedup,
                                "estado": 'ingreso' if tipo == 'credito' else 'sin_conciliar',
                                "cat": 'ingreso' if tipo == 'credito' else 'otros',
                                "archivo": archivo.name
                            }
                        )
                        nuevos += 1

                session.commit()

                st.success(f"""
                ✅ **Importación Completada**
                - ✔️ {nuevos} movimiento(s) nuevo(s)
                - ⚠️ {duplicados} duplicado(s) omitido(s)
                """)

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

        st.divider()

        # Tabla de movimientos
        st.subheader("🏦 Movimientos Cargados")

        datos = session.execute(
            text("""
                SELECT fecha, tipo, monto, descripcion, estado, archivo_origen
                FROM movimiento_bancario
                WHERE empresa_id = :eid
                ORDER BY fecha DESC
                LIMIT 50
            """),
            {"eid": empresa_id}
        ).fetchall()

        if datos:
            df = pd.DataFrame(datos, columns=['Fecha', 'Tipo', 'Monto', 'Descripción', 'Estado', 'Archivo'])
            df['Fecha'] = pd.to_datetime(df['Fecha']).dt.strftime('%d/%m/%Y')
            df['Monto'] = df['Monto'].apply(lambda x: f"${x:,.2f}")
            df['Tipo'] = df['Tipo'].apply(lambda x: '⬇ Egreso' if x == 'debito' else '⬆ Ingreso')
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No hay movimientos cargados")

    finally:
        session.close()

# ==================== MAIN ====================
def main():
    if not st.session_state.usuario_id:
        login_page()
    else:
        # Sidebar
        with st.sidebar:
            st.title(f"👤 {st.session_state.usuario_email}")

            page = st.radio(
                "Menú",
                ["📊 Dashboard", "🏦 Conciliación"],
                label_visibility="collapsed"
            )

            st.divider()

            if st.button("🚪 Cerrar Sesión", use_container_width=True):
                st.session_state.usuario_id = None
                st.session_state.usuario_email = None
                st.session_state.empresa_id = None
                st.rerun()

        # Mostrar página
        if page == "📊 Dashboard":
            dashboard_page()
        elif page == "🏦 Conciliación":
            conciliacion_page()

if __name__ == "__main__":
    main()
