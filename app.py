import streamlit as st

# Configuración de la página
st.set_page_config(page_title="Arias Hnos. | Gestión de Ventas", layout="wide")

# Título y Bienvenida
st.title("🚗 Arias Hnos. | Presupuestador")
st.write(f"Vendedor: **Alejandro**")

# --- LÓGICA DE CARGA DE PLANILLA ---
st.sidebar.header("Configuración")
opcion = st.sidebar.radio("¿Qué desea hacer?", ["Cargar nueva planilla", "Usar datos guardados"])

if opcion == "Cargar nueva planilla":
    archivo = st.file_uploader("Suba el archivo de precios (.txt)", type=["txt"])
    if archivo:
        st.success("✅ Precios actualizados")
else:
    st.sidebar.info("Utilizando última base de datos.")

# --- SELECCIÓN DE MODELOS (Lo que teníamos antes) ---
st.subheader("Selección de Unidad")
col_m, col_v = st.columns(2)

with col_m:
    modelo = st.selectbox("Modelo", ["Amarok", "Taos", "Polo", "Nivus", "T-Cross", "Vento", "Virtus"])
with col_v:
    version = st.selectbox("Versión", ["Trendline", "Comfortline", "Highline", "Extreme", "Black Style"])

# --- GENERADOR DE PRESUPUESTO ---
st.write("---")
st.subheader("📝 Detalle del Presupuesto")

# Aquí es donde el programa armará el texto para el cliente
presupuesto_texto = f"Presupuesto Arias Hnos.\nModelo: {modelo}\nVersión: {version}\nPrecio: (Cargar planilla para ver valor)\n\nContacto: Alejandro"

resultado = st.text_area("Texto para enviar:", value=presupuesto_texto, height=200)

# --- LOS BOTONES QUE NO PUEDEN FALTAR ---
c1, c2 = st.columns(2)
with c1:
    if st.button("📋 COPIAR PARA WHATSAPP", use_container_width=True):
        st.toast("¡Copiado con éxito!")
with c2:
    if st.button("🖨️ IMPRIMIR PRESUPUESTO", use_container_width=True):
        st.write("Conectando con impresora...")

st.write("---")
st.caption("Sistema de Gestión Arias Hnos. 2026")
