import streamlit as st
import pandas as pd
import easyocr
import numpy as np
from PIL import Image
import re

st.set_page_config(page_title="Gestor Arias Hnos.", page_icon="🚗")
st.title("🚗 Arias Hnos. | Paso 1: Suscripción (Actualización Real)")

@st.cache_resource
def cargar_lector():
    return easyocr.Reader(['es'])

reader = cargar_lector()

def limpiar_suscripcion(texto):
    num = re.sub(r'[^0-9.]', '', texto)
    if len(num) >= 7 and num.startswith(('5', '8')):
        num = num[1:]
    return f"${num}"

if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame({
        "Modelo": ["TERA", "VIRTUS", "T-CROSS", "NIVUS", "AMAROK", "TAOS"],
        "Suscripción": ["$0"]*6
    })

archivo = st.file_uploader("Subí la planilla para actualizar precios", type=['jpg', 'jpeg', 'png'])

if archivo:
    # --- NOVEDAD: Reiniciamos la columna para que no queden precios viejos --- [cite: 2026-01-27]
    st.session_state.df["Suscripción"] = "$0"
    
    img = Image.open(archivo)
    with st.spinner('🤖 Leyendo precios nuevos de la foto...'):
        res = reader.readtext(np.array(img), detail=0)
        modelos_map = {"TERA": 0, "VIRTUS": 1, "T-CROSS": 2, "NIVUS": 3, "AMAROK": 4, "TAOS": 5}
        
        for i, texto in enumerate(res):
            t_up = texto.upper()
            for mod, fila in modelos_map.items():
                if mod in t_up:
                    for j in range(i+1, min(i+10, len(res))):
                        if "Suscrip" in res[j] and j+1 < len(res):
                            precio_nuevo = limpiar_suscripcion(res[j+1])
                            # Aquí es donde 'pisamos' el dato viejo con el nuevo [cite: 2026-01-27]
                            st.session_state.df.at[fila, "Suscripción"] = precio_nuevo
                            break

st.subheader("📊 Control de Precios Actualizados")
st.table(st.session_state.df)
