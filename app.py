import streamlit as st
import pandas as pd
import easyocr
import numpy as np
from PIL import Image
import re

st.set_page_config(page_title="Gestor Arias Hnos.", page_icon="🚗")
st.title("🚗 Arias Hnos. | Paso 1: Suscripción")

@st.cache_resource
def cargar_lector():
    return easyocr.Reader(['es'])

reader = cargar_lector()

# Función especial para limpiar el error del signo $ [cite: 2026-01-27]
def limpiar_suscripcion(texto):
    # Quitamos todo lo que no sea número o punto
    num = re.sub(r'[^0-9.]', '', texto)
    # Si el precio empieza con 5 u 8 y es muy largo, borramos ese primer número
    if len(num) >= 7 and num.startswith(('5', '8')):
        num = num[1:]
    return f"${num}"

if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame({
        "Modelo": ["TERA", "VIRTUS", "T-CROSS", "NIVUS", "AMAROK", "TAOS"],
        "Suscripción": ["$0"]*6
    })

archivo = st.file_uploader("Subí la planilla para probar la Suscripción", type=['jpg', 'jpeg', 'png'])

if archivo:
    img = Image.open(archivo)
    with st.spinner('🤖 Analizando Suscripciones...'):
        res = reader.readtext(np.array(img), detail=0)
        modelos_map = {"TERA": 0, "VIRTUS": 1, "T-CROSS": 2, "NIVUS": 3, "AMAROK": 4, "TAOS": 5}
        
        for i, texto in enumerate(res):
            t_up = texto.upper()
            for mod, fila in modelos_map.items():
                if mod in t_up:
                    # Buscamos la palabra Suscripción en los siguientes 10 renglones
                    for j in range(i+1, min(i+10, len(res))):
                        if "Suscrip" in res[j] and j+1 < len(res):
                            # El precio es el renglón de abajo
                            precio_sucio = res[j+1]
                            st.session_state.df.at[fila, "Suscripción"] = limpiar_suscripcion(precio_sucio)
                            break

st.subheader("📊 Control de Suscripciones")
st.table(st.session_state.df)
