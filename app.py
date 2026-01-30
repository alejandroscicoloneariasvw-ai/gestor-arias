import streamlit as st

# Configuración de página
st.set_page_config(page_title="Arias Hnos. | Gestión de Ventas", layout="centered")

# Título Principal
st.title("🚗 Arias Hnos. | Presupuestador")
st.write("Bienvenido, Alejandro.")

# --- LÓGICA DE CARGA ---
st.subheader("Configuración de Datos")
modo = st.radio("¿Qué desea hacer?", ["Cargar nueva planilla", "Usar datos guardados"])

if modo == "Cargar nueva planilla":
    archivo = st.file_uploader("Suba el archivo de la planilla (TXT o PDF)", type=["txt", "pdf"])
    if archivo:
        st.success("Archivo recibido correctamente.")
else:
    st.info("Usando los datos de la última planilla cargada.")

# --- ESPACIO PARA EL PRESUPUESTO ---
st.write("---")
st.subheader("Generador de Presupuesto")
st.text_area("Resultado del presupuesto:", "Aquí aparecerán los datos para el cliente...", height=200)

# --- BOTONES QUE PEDISTE ---
col1, col2 = st.columns(2)
with col1:
    if st.button("📋 Copiar Presupuesto"):
        st.toast("¡Copiado al portapapeles!")
with col2:
    if st.button("🖨️ Imprimir"):
        st.write("Abriendo menú de impresión...")

st.write("---")
st.caption("Gestor Arias v2.0 - 2026")
