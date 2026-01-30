import streamlit as st

# Configuración de la página
st.set_page_config(page_title="Arias Hnos. | Gestión de Ventas", layout="centered")

# Título con estilo
st.title("🚗 Arias Hnos. | Presupuestador")
st.write(f"Sesión activa: **Alejandro**")

# --- SECCIÓN DE CARGA DE DATOS ---
st.markdown("### 📊 Datos de la Planilla")
opcion = st.radio(
    "Seleccione una opción:",
    ["Usar datos guardados", "Cargar nueva planilla"],
    help="Elija si desea subir una foto/PDF nuevo o usar la última versión cargada."
)

if opcion == "Cargar nueva planilla":
    archivo = st.file_uploader("Subir foto o PDF de la planilla", type=["pdf", "jpg", "jpeg", "png", "txt"])
    if archivo:
        st.success("✅ Archivo cargado correctamente.")
else:
    st.info("ℹ️ Utilizando los datos de la última planilla cargada.")

st.write("---")

# --- ÁREA DE TRABAJO ---
st.markdown("### 📝 Generador de Presupuesto")
resultado = st.text_area(
    "Presupuesto para el cliente:", 
    placeholder="Aquí aparecerán los precios calculados...",
    height=250
)

# --- BOTONES DE ACCIÓN ---
col1, col2 = st.columns(2)

with col1:
    if st.button("📋 Copiar Presupuesto", use_container_width=True):
        if resultado:
            st.toast("¡Copiado al portapapeles!")
        else:
            st.warning("No hay nada para copiar.")

with col2:
    if st.button("🖨️ Imprimir", use_container_width=True):
        st.write("Abriendo opciones de impresión...")

# Pie de página
st.write("---")
st.caption("Gestor Arias Hnos. v2.0 | 2026")  
