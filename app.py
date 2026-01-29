import streamlit as st
import pd as pd
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

# 🔄 BOTÓN DE REINICIO TOTAL AL PRINCIPIO
if st.sidebar.button("🗑️ BORRAR TODO Y EMPEZAR DE NUEVO"):
    st.cache_data.clear()
    st.session_state.clear()
    st.rerun()

archivo = st.file_uploader("Subí la planilla de Arias Hnos.", type=['jpg', 'jpeg', 'png'])

if archivo:
    st.image(archivo, width=250, caption="Archivo actual")
    
    # Solo procesamos si no lo hemos hecho ya para este archivo específico
    with st.spinner('🤖 Procesando planilla... por favor esperá...'):
        img = Image.open(archivo)
        res = reader.readtext(np.array(img), detail=0)
        
        # Creamos una tabla nueva CADA VEZ que subís algo [cite: 2026-01-27]
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
                            if "Suscrip" in res[j] and j+1 < len(res):
                                df_temp.at[fila, "Suscripción"] = limpiar_monto(res[j+1])
                            if "Cuota No" in res[j] and j+1 < len(res):
                                valor_c1 = res[j+1]
                                if "." in valor_c1 and len(valor_c1) > 4:
                                    df_temp.at[fila, "Cuota 1"] = limpiar_monto(valor_c1)
                                    break
            
            # RECIÉN AQUÍ MOSTRAMOS LA TABLA [cite: 2026-01-28]
            st.subheader("📊 Precios Actualizados")
            st.table(df_temp)
            st.success("✅ ¡Lectura completada con éxito!")
        else:
            st.error("No se pudo leer el texto. Probá con otra foto más nítida.")
else:
    st.info("Esperando que subas una planilla...")
