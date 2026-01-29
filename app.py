import streamlit as st
import pandas as pd
import easyocr
import numpy as np
from PIL import Image
import re

st.set_page_config(page_title="Arias Hnos. | Lector Pro", layout="wide")
st.title("🚗 Arias Hnos. | Sistema de Precios")

@st.cache_resource
def get_reader():
    return easyocr.Reader(['es'])

reader = get_reader()

def limpiar_precio(texto):
    # Solo dejamos números y puntos
    num = re.sub(r'[^0-9.]', '', texto)
    # Un precio real de Arias Hnos tiene al menos 5 dígitos (ej: 490.000)
    # Si tiene 2 o 3 dígitos, es un error (ej: 84 meses) [cite: 2026-01-27]
    if len(num.replace('.', '')) < 5:
        return None
    # Quitamos el 5 u 8 rebelde del principio si el número es muy largo [cite: 2026-01-27]
    if len(num.replace('.', '')) >= 7 and num.startswith(('5', '8', '3')):
        num = num[1:]
    return f"${num}"

# --- INTERFAZ ---
archivo = st.file_uploader("Subí la planilla", type=['jpg', 'jpeg', 'png'])

if archivo:
    img = Image.open(archivo)
    st.image(img, width=400)
    
    with st.spinner('🤖 Procesando datos...'):
        res = reader.readtext(np.array(img), detail=0)
        
        # Diccionario para guardar lo que encontremos
        modelos = ["TERA", "VIRTUS", "T-CROSS", "NIVUS", "AMAROK", "TAOS"]
        datos = {m: {"Susc": "$0", "C1": "$0"} for m in modelos}
        
        modelo_actual = None
        
        for i, texto in enumerate(res):
            t_up = texto.upper()
            
            # 1. Detectar el Modelo
            for mod in modelos:
                if mod in t_up:
                    modelo_actual = mod
            
            # 2. Si tenemos un modelo, buscamos sus precios debajo [cite: 2026-01-27]
            if modelo_actual:
                if "SUSC" in t_up and i+1 < len(res):
                    p = limpiar_precio(res[i+1])
                    if p: datos[modelo_actual]["Susc"] = p
                
                if "CUOTA N" in t_up and i+1 < len(res):
                    p = limpiar_precio(res[i+1])
                    if p: datos[modelo_actual]["C1"] = p

        # Crear tabla
        df = pd.DataFrame([
            {"Modelo": m, "Suscripción": datos[m]["Susc"], "Cuota 1": datos[m]["C1"]}
            for m in modelos
        ])
        
        st.subheader("📊 Tabla de la Foto Actual")
        st.table(df)

# --- BOTÓN DE CONTROL --- [cite: 2026-01-27]
if st.sidebar.button("🗑️ LIMPIAR TODO"):
    st.cache_data.clear()
    st.rerun()

# --- DEBUG: Para que Alejandro vea qué lee la IA si falla ---
if st.checkbox("🔍 Ver qué está leyendo la IA (Modo Técnico)"):
    if archivo:
        st.write(res)
