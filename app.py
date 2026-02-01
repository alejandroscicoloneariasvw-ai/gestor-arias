import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN DE INTERFAZ ---
st.set_page_config(page_title="Scicolone Data System", layout="wide")

# Estilo para botones y diseño limpio
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; font-weight: bold; }
    hr { margin-top: 1rem; margin-bottom: 1rem; }
    </style>
    """, unsafe_allow_html=True)

# --- ENCABEZADO PROFESIONAL (Versión Final) ---
st.title("📊 Sistema de Procesamiento de Planillas")
st.markdown("<p style='font-size: 1.2rem; color: #666;'>Data Architecture & Development by <b>Alejandro Scicolone</b></p>", unsafe_allow_html=True)
st.divider()

# --- LÓGICA DE CARGA (Pregunta inicial) ---
opcion_carga = st.radio(
    "**Gestión de planilla:**",
    ["Utilizar datos guardados (Última sesión)", "Cargar una planilla nueva (Foto/PDF)"],
    index=0,
    horizontal=True
)

if opcion_carga == "Cargar una planilla nueva (Foto/PDF)":
    archivo_nuevo = st.file_uploader("Subir archivo", type=['pdf', 'png', 'jpg', 'jpeg'])
    if archivo_nuevo:
        st.success(f"Planilla '{archivo_nuevo.name}' lista para procesar.")
else:
    st.info("Cargando la última base de datos almacenada en el sistema...")

st.divider()

# --- ESPACIO DE TRABAJO ---
# Simulamos los datos que estarían en la planilla
st.subheader("Visualización de Datos")
datos_ejemplo = pd.DataFrame({
    "Campo": ["Fecha de Carga", "Responsable", "Estado del Registro"],
    "Detalle": [datetime.now().strftime("%d/%m/%Y"), "A. Scicolone", "Verificado"]
})
st.table(datos_ejemplo)

# --- BOTONES DE COPIAR E IMPRIMIR ---
col1, col2 = st.columns(2)

with col1:
    if st.button("📋 Copiar Datos"):
        st.toast("Copiado al portapapeles con éxito.")

with col2:
    # Lógica de impresión/descarga
    st.download_button(
        label="🖨️ Imprimir Planilla",
        data=datos_ejemplo.to_csv().encode('utf-8'),
        file_name=f"Planilla_{datetime.now().strftime('%H%M%S')}.pdf",
        mime="application/pdf"
    )

st.markdown("---")
st.caption("Scicolone Systems | Enterprise Solution 2026")
