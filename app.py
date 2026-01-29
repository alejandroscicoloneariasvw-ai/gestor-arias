import streamlit as st
import pandas as pd
import easyocr
import numpy as np
from PIL import Image
import re

st.set_page_config(page_title="Gestor Arias Hnos.", page_icon="🚗")
st.title("🚗 Arias Hnos. | Lector Pro")

@st.cache_resource
def cargar_lector():
    return easyocr.Reader(['es'])

reader = cargar_lector()

def limpiar_monto(texto):
    num = re.sub(r'[^0-9.]', '', texto)
    if len(num) >= 7 and num.startswith(('5', '8', '3')):
        num = num[1:]
    return f"${num}" if num else "$0"

# Botón de reinicio en la barra lateral
if st.sidebar.button("🗑️ BORRAR TODO Y EMPEZAR"):
    st.cache_data.clear()
    st.session_state.clear()
    st.rerun()

archivo = st.file_uploader("Subí la planilla de Arias Hnos.", type=['jpg', 'jpeg', 'png'])

if archivo:
    st.image(archivo, width=250, caption="Planilla para procesar")
    
    with st.spinner('🤖 Procesando planilla... por favor esperá...'):
        img = Image.open(archivo)
        res = reader.readtext(np.array(img), detail=0)
        
        # Estructura de la tabla [cite: 2026-01-27]
        datos_nuevos = {
            "Modelo": ["TERA", "VIRTUS", "T-CROSS", "NIVUS", "AMAROK", "TAOS"],
            "Suscripción": ["$0"]*6,
            "Cuota 1": ["$0"]*6
        }
        df_temp = pd.DataFrame(datos_nuevos)
        
        if len(res) > 0:
            modelos_map = {"TERA": 0, "VIRTUS": 1, "T-CROSS": 2, "NIVUS": 3, "AMAROK": 4, "TAOS": 5}
            for i, texto in enumerate(res):
                t_up = texto.upper()
                for mod, fila in modelos_map.items():
                    if mod in t_up:
                        for j in range(i+1, min(i+20, len(res))):
                            # Captura Suscripción [cite: 2026-01-27]
                            if "Suscrip" in res[j] and j+1 < len(res):
                                df_temp.at[fila, "Suscripción"] = limpiar_monto(res[j+1])
                            # Captura Cuota 1 [cite: 2026-01-27]
                            if "Cuota No" in res[j] and j+1 < len(res):
                                valor_c1 = res[j+1]
                                if "." in valor_c1 and len(valor_c1) > 4:
                                    df_temp.at[fila, "Cuota 1"] = limpiar_monto(valor_c1)
                                    break
            
            st.subheader("📊 Precios Detectados")
            st.table(df_temp)
            st.success("✅ ¡Lectura terminada!")
        else:
            st.error("No se detectó texto. Intentá con otra foto.")
else:
    st.info("Esperando planilla...")
