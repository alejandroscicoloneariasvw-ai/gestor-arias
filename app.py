import streamlit as st
import pandas as pd
import easyocr
import numpy as np
from PIL import Image

st.set_page_config(page_title="Scanner Arias Hnos.", page_icon="🔍")
st.title("🔍 Scanner de Planilla | Arias Hnos.")

@st.cache_resource
def cargar_lector():
    # Cargamos el lector una sola vez
    return easyocr.Reader(['es'])

reader = cargar_lector()

# 1. Botón para cargar la imagen [cite: 2026-01-27]
archivo = st.file_uploader("Subí la planilla para analizar la lectura", type=['jpg', 'jpeg', 'png'])

if archivo:
    # 2. Mostrar la imagen cargada [cite: 2026-01-27]
    img = Image.open(archivo)
    st.image(img, caption="Imagen cargada para el análisis", use_container_width=True)
    
    with st.spinner('🤖 Leyendo planilla...'):
        img_np = np.array(img)
        # Obtenemos la lectura completa
        resultados = reader.readtext(img_np, detail=0) # detail=0 devuelve solo el texto
        
        st.divider()
        st.subheader("📝 Texto detectado (en orden de lectura):")
        
        # 3. Mostrar lo que va leyendo renglón por renglón
        # Esto nos va a servir para ver dónde están los precios [cite: 2026-01-28]
        for i, texto in enumerate(resultados):
            st.write(f"**Renglón {i}:** {texto}")

else:
    st.info("Esperando que cargues una planilla para empezar el escaneo...")
