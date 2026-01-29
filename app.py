import streamlit as st
import pandas as pd
import easyocr
import numpy as np
from PIL import Image
import re

st.set_page_config(page_title="Gestor Arias Hnos.", page_icon="🚗")
st.title("🚗 Arias Hnos. | Lector Rápido")

# ⚡ Función para que el lector no se cargue mil veces
@st.cache_resource
def cargar_lector():
    return easyocr.Reader(['es'])

reader = cargar_lector()

# ⚡ Función para procesar la imagen sin trabar el servidor
@st.cache_data
def procesar_planilla(imagen_bytes):
    img = Image.open(imagen_bytes)
    res = reader.readtext(np.array(img), detail=0)
    return res

def limpiar_monto(texto):
    num = re.sub(r'[^0-9.]', '', texto)
    if len(num) >= 7 and num.startswith(('5', '8', '3')):
        num = num[1:]
    return f"${num}" if num else "$0"

if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame({
        "Modelo": ["TERA", "VIRTUS", "T-CROSS", "NIVUS", "AMAROK", "TAOS"],
        "Suscripción": ["$0"]*6,
        "Cuota 1": ["$0"]*6
    })

archivo = st.file_uploader("Subí la planilla", type=['jpg', 'jpeg', 'png'], key="lector_unio")

if archivo:
    # Mostramos la imagen chiquita para que sepa que cargó
    st.image(archivo, width=200)
    
    with st.spinner('🤖 Leyendo rápido...'):
        # Usamos la función optimizada
        res = procesar_planilla(archivo)
        
        modelos_map = {"TERA": 0, "VIRTUS": 1, "T-CROSS": 2, "NIVUS": 3, "AMAROK": 4, "TAOS": 5}
        
        if len(res) > 0:
            for i, texto in enumerate(res):
                t_up = texto.upper()
                for mod, fila in modelos_map.items():
                    if mod in t_up:
                        for j in range(i+1, min(i+20, len(res))):
                            if "Suscrip" in res[j] and j+1 < len(res):
                                st.session_state.df.at[fila, "Suscripción"] = limpiar_monto(res[j+1])
                            if "Cuota No" in res[j] and j+1 < len(res):
                                valor_c1 = res[j+1]
                                if "." in valor_c1 and len(valor_c1) > 4:
                                    st.session_state.df.at[fila, "Cuota 1"] = limpiar_monto(valor_c1)
                                    break

st.subheader("📊 Precios Detectados")
st.table(st.session_state.df)

# Un botón de "Limpiar Todo" por si las dudas
if st.button("🗑️ Limpiar y Nueva Carga"):
    st.cache_data.clear() # Borra la memoria caché
    st.session_state.clear()
    st.rerun()
