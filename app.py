import streamlit as st
import pandas as pd
import easyocr
import numpy as np
from PIL import Image
import re

st.set_page_config(page_title="Gestor Arias Hnos.", page_icon="🚗")
st.title("🚗 Arias Hnos. | Verificación de Cambios")

@st.cache_resource
def cargar_lector():
    return easyocr.Reader(['es'])

reader = cargar_lector()

def limpiar_monto(texto):
    num = re.sub(r'[^0-9.]', '', texto)
    if len(num) >= 7 and num.startswith(('5', '8', '3')):
        num = num[1:]
    return f"${num}" if num else "$0"

# Inicializamos la tabla
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame({
        "Modelo": ["TERA", "VIRTUS", "T-CROSS", "NIVUS", "AMAROK", "TAOS"],
        "Suscripción": ["$0"]*6,
        "Cuota 1": ["$0"]*6
    })

archivo = st.file_uploader("Subí una planilla (Verificá que los precios cambien)", type=['jpg', 'jpeg', 'png'])

if archivo:
    # 🔄 FORZAMOS REINICIO: Si hay un archivo nuevo, "vaciamos" la tabla para asegurar que no hay datos viejos
    if 'ultimo_archivo' not in st.session_state or st.session_state.ultimo_archivo != archivo.name:
        st.session_state.df["Suscripción"] = "⏳..."
        st.session_state.df["Cuota 1"] = "⏳..."
        st.session_state.ultimo_archivo = archivo.name

    img = Image.open(archivo)
    st.image(img, width=300)
    
    with st.spinner('🤖 Actualizando datos desde la nueva imagen...'):
        res = reader.readtext(np.array(img), detail=0)
        modelos_map = {"TERA": 0, "VIRTUS": 1, "T-CROSS": 2, "NIVUS": 3, "AMAROK": 4, "TAOS": 5}
        
        if len(res) > 0:
            for i, texto in enumerate(res):
                t_up = texto.upper()
                for mod, fila in modelos_map.items():
                    if mod in t_up:
                        for j in range(i+1, min(i+20, len(res))):
                            # Suscripción
                            if "Suscrip" in res[j] and j+1 < len(res):
                                st.session_state.df.at[fila, "Suscripción"] = limpiar_monto(res[j+1])
                            # Cuota 1
                            if "Cuota No" in res[j] and j+1 < len(res):
                                valor_c1 = res[j+1]
                                if "." in valor_c1 and len(valor_c1) > 4:
                                    st.session_state.df.at[fila, "Cuota 1"] = limpiar_monto(valor_c1)
                                    break

st.subheader("📊 Tabla de Precios (Foto Actual)")
st.table(st.session_state.df)

if st.button("🗑️ Borrar Memoria"):
    st.session_state.clear()
    st.rerun()
