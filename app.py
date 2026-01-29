import streamlit as st
import pandas as pd
import easyocr
import numpy as np
from PIL import Image
import re

st.set_page_config(page_title="Arias Hnos. | Lector Pro", layout="wide")
st.title("🚗 Arias Hnos. | Sistema Inteligente")

@st.cache_resource
def get_reader():
    return easyocr.Reader(['es'])

reader = get_reader()

def limpiar_precio_real(texto):
    # Solo dejamos números
    num = re.sub(r'[^0-9]', '', texto)
    # Si el precio es menor a 5 dígitos (ej: 84), es basura, lo ignoramos [cite: 2026-01-27]
    if len(num) < 5:
        return None
    # Si empieza con 5 u 8 y es muy largo, sacamos el primer dígito [cite: 2026-01-27]
    if len(num) >= 7 and num.startswith(('5', '8', '3')):
        num = num[1:]
    
    # Formateamos con puntos para que quede lindo
    if len(num) > 3:
        num_formateado = f"{int(num):,}".replace(",", ".")
        return f"${num_formateado}"
    return f"${num}"

# --- INTERFAZ ---
archivo = st.file_uploader("Subí cualquier planilla (Amarilla o Color)", type=['jpg', 'jpeg', 'png'])

if archivo:
    img = Image.open(archivo)
    st.image(img, width=400)
    
    with st.spinner('🤖 Analizando datos...'):
        res = reader.readtext(np.array(img), detail=0)
        
        modelos = ["TERA", "VIRTUS", "T-CROSS", "NIVUS", "AMAROK", "TAOS"]
        # Diccionario temporal para guardar lo que vamos encontrando
        datos_actuales = {m: {"Susc": "$0", "C1": "$0"} for m in modelos}
        
        modelo_en_foco = None
        
        for i, texto in enumerate(res):
            t_up = texto.upper()
            
            # 1. Identificar de qué auto estamos hablando
            for mod in modelos:
                if mod in t_up:
                    modelo_en_foco = mod
            
            # 2. Si tenemos un auto identificado, buscamos sus precios
            if modelo_en_foco:
                # Buscamos Suscripción (muy flexible) [cite: 2026-01-27]
                if any(x in t_up for x in ["SUSC", "SCRIP", "SU5C"]):
                    # El precio suele estar en los siguientes 2 renglones
                    for k in range(1, 3):
                        if i+k < len(res):
                            p = limpiar_precio_real(res[i+k])
                            if p:
                                datos_actuales[modelo_en_foco]["Susc"] = p
                                break
                
                # Buscamos Cuota 1
                if any(x in t_up for x in ["CUOTA N", "CUOTAN", "CU0TA"]):
                    for k in range(1, 3):
                        if i+k < len(res):
                            p = limpiar_precio_real(res[i+k])
                            if p:
                                datos_actuales[modelo_en_foco]["C1"] = p
                                break

        # Armamos la tabla final
        df_final = pd.DataFrame([
            {"Modelo": m, "Suscripción": datos_actuales[m]["Susc"], "Cuota 1": datos_actuales[m]["C1"]}
            for m in modelos
        ])
        
        st.subheader("📊 Datos Detectados")
        st.table(df_final)

# Botón lateral por si querés resetear manual
if st.sidebar.button("🗑️ LIMPIAR MEMORIA"):
    st.cache_resource.clear()
    st.rerun()
