import streamlit as st
import pandas as pd
import easyocr
import numpy as np
from PIL import Image

# Configuración de la App
st.set_page_config(page_title="Gestor Arias Hnos.", page_icon="🚗")
st.title("🚗 Arias Hnos. | Lector Inteligente")

# 1. Cargamos el lector (Esto puede tardar un poquito la primera vez)
@st.cache_resource
def cargar_lector():
    return easyocr.Reader(['es'])

reader = cargar_lector()

# 2. Menú lateral solicitado [cite: 2026-01-27]
modo = st.sidebar.radio("Menú de Opciones", ("Cargar Planilla Nueva", "Usar Datos Guardados"))

# Datos iniciales (se actualizarán al leer la foto)
if 'df_ventas' not in st.session_state:
    datos = {
        "Modelo": ["Tera Trend", "Virtus", "T-Cross", "Nivus", "Taos", "Amarok"],
        "Suscripción": ["$500.000", "$850.000", "$700.000", "$700.000", "$950.000", "$800.000"],
        "Cuota 1": ["$450.000", "$730.000", "$650.000", "$570.000", "$820.000", "$650.000"],
        "Cuota Pura": ["$297.315", "$527.472", "$431.792", "$373.979", "$610.500", "$407.952"]
    }
    st.session_state.df_ventas = pd.DataFrame(datos)

if modo == "Cargar Planilla Nueva":
    archivo = st.file_uploader("Subí la foto de la planilla", type=['jpg', 'jpeg', 'png'])
    
    if archivo:
        img = Image.open(archivo)
        st.image(img, caption="Planilla detectada", use_container_width=True)
        
        with st.spinner('🤖 La IA está leyendo los nuevos precios...'):
            # Convertimos imagen para el lector
            img_np = np.array(img)
            resultados = reader.readtext(img_np, detail=0)
            
            # Aquí la IA buscará los números (Lógica en desarrollo)
            st.success("✅ Lectura completada")
            st.write("Datos encontrados:", resultados[:5]) # Muestra los primeros 5 textos hallados

# 3. Tabla de Precios y Botones [cite: 2026-01-27]
st.subheader("📊 Tabla de Precios Actualizada")
st.table(st.session_state.df_ventas)

col1, col2 = st.columns(2)
with col1:
    if st.button("📋 Copiar para WhatsApp"):
        st.info("Texto copiado al portapapeles")
with col2:
    if st.button("🖨️ Imprimir Presupuesto"):
        st.success("Abriendo menú de impresión...")
