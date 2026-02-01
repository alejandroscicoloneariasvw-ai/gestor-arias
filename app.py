import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Scicolone Data System", 
    page_icon="📊", 
    layout="wide"
)

# --- 2. ESTILOS CSS (Para que los botones y el diseño sean Pro) ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3.5em;
        font-weight: bold;
        transition: all 0.3s;
        border: 1px solid #d1d5db;
    }
    .stButton>button:hover {
        border-color: #007bff;
        color: #007bff;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        text-align: center;
        color: gray;
        font-size: 0.8rem;
        padding: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. ENCABEZADO PROFESIONAL ---
st.title("📊 Sistema de Procesamiento de Planillas")
st.markdown("<p style='font-size: 1.2rem; color: #555;'>Data Architecture & Development by <b>Alejandro Scicolone</b></p>", unsafe_allow_html=True)
st.divider()

# --- 4. LÓGICA DE CARGA DE DATOS ---
col_menu, col_status = st.columns([2, 1])

with col_menu:
    opcion = st.radio(
        "**Gestión de Datos:**",
        ["Utilizar última planilla cargada", "Cargar nueva planilla (Foto o PDF)"],
        index=0,
        horizontal=True
    )

# Simulamos una base de datos guardada
if "datos" not in st.session_state:
    st.session_state.datos = pd.DataFrame({
        "ID": [1, 2],
        "Descripción": ["Ejemplo de Carga", "Dato Histórico"],
        "Estado": ["Procesado", "Guardado"]
    })

if opcion == "Cargar nueva planilla (Foto o PDF)":
    archivo = st.file_uploader("Seleccione el archivo", type=['pdf', 'png', 'jpg', 'jpeg'])
    if archivo:
        st.success(f"✅ '{archivo.name}' cargado con éxito.")
        # Aquí iría la lógica de OCR o lectura de PDF
else:
    st.info("📂 Utilizando registros de la última sesión guardada.")

st.divider()

# --- 5. ÁREA DE TRABAJO (VISUALIZACIÓN) ---
st.subheader("Contenido de la Planilla")
st.dataframe(st.session_state.datos, use_container_width=True)

# --- 6. BOTONES DE ACCIÓN (COPIAR E IMPRIMIR) ---
st.write("---")
col_copy, col_print = st.columns(2)

with col_copy:
    if st.button("📋 Copiar Datos al Portapapeles"):
        # Simulamos la copia (en Streamlit web esto se suele manejar con descarga o avisos)
        st.toast("Datos copiados al portapapeles (Simulado)", icon="✅")

with col_print:
    # Generamos un CSV o texto para "Imprimir/Descargar"
    csv = st.session_state.datos.to_csv(index=False).encode('utf-8')
    
    st.download_button(
        label="🖨️ Generar PDF / Imprimir",
        data=csv,
        file_name=f"Planilla_Scicolone_{datetime.now().strftime('%d_%m_%Y')}.csv",
        mime="text/csv",
        help="Haz clic para descargar y enviar a la impresora"
    )

# Pie de página sutil
st.markdown("<div class='footer'>Scicolone Systems © 2026 | Enterprise Edition</div>", unsafe_allow_html=True)
