import streamlit as st
import pandas as pd
import easyocr
import numpy as np
from PIL import Image, ImageOps, ImageEnhance
import re

st.set_page_config(page_title="Arias Hnos. | Lector Pro", layout="wide")
st.title("🚗 Arias Hnos. | Sistema de Precios")

@st.cache_resource
def get_reader():
    return easyocr.Reader(['es'])

reader = get_reader()

def limpiar_precio(texto):
    # Solo nos quedan los números [cite: 2026-01-27]
    num = re.sub(r'[^0-9]', '', texto)
    if not num or len(num) < 5 or len(num) > 7: 
        return None
    # Corrección del signo $ mal leído [cite: 2026-01-27]
    if len(num) == 7 and num.startswith(('5', '8', '3')):
        num = num[1:]
    return int(num)

# --- ESCUDO ANTI-ERROR ROJO ---
if 'memoria_final' not in st.session_state:
    st.session_state.memoria_final = None

opcion = st.radio("Acción:", ["Cargar una planilla nueva", "Usar datos guardados"])

if opcion == "Cargar una planilla nueva":
    archivo = st.file_uploader("Subí la planilla", type=['jpg', 'jpeg', 'png'])
    if archivo:
        img_original = Image.open(archivo)
        with st.spinner('🤖 Analizando planilla...'):
            # En la roja, procesamos la imagen normal para no quemar el texto
            res = reader.readtext(np.array(img_original), detail=0)
            
            modelos = ["TERA", "VIRTUS", "T-CROSS", "NIVUS", "AMAROK", "TAOS"]
            datos = {m: {"Susc": 0, "C1": 0} for m in modelos}
            
            for i, texto in enumerate(res):
                t_up = texto.upper()
                for m in modelos:
                    if m in t_up:
                        # Cuando encontramos el modelo, miramos los próximos 15 bloques de texto [cite: 2026-01-27]
                        encontrados = []
                        for j in range(1, 15):
                            if i + j < len(res):
                                p = limpiar_precio(res[i+j])
                                if p: encontrados.append(p)
                        
                        # El primer número suele ser la Suscripción y el segundo la Cuota 1 [cite: 2026-01-27]
                        if len(encontrados) >= 2:
                            datos[m]["Susc"] = encontrados[0]
                            datos[m]["C1"] = encontrados[1]
                        elif len(encontrados) == 1:
                            datos[m]["C1"] = encontrados[0]

            final = {m: {
                "Susc": f"${datos[m]['Susc']:,}".replace(",", ".") if datos[m]["Susc"] > 0 else "$0",
                "C1": f"${datos[m]['C1']:,}".replace(",", ".") if datos[m]["C1"] > 0 else "$0"
            } for m in modelos}
            st.session_state.memoria_final = final
            st.success("✅ Análisis completo.")

# --- RESULTADOS SEGUROS ---
if st.session_state.memoria_final is not None:
    d = st.session_state.memoria_final
    modelos_lista = ["TERA", "VIRTUS", "T-CROSS", "NIVUS", "AMAROK", "TAOS"]
    df = pd.DataFrame([{"Modelo": m, "Suscripción": d[m]["Susc"], "Cuota 1": d[m]["C1"]} for m in modelos_lista])
    st.table(df)
    
    st.divider()
    sel = st.selectbox("Elegí el modelo:", modelos_lista)
    msj = f"*Arias Hnos.*\n*Auto:* {sel}\n✅ *Suscripción:* {d[sel]['Susc']}\n✅ *Cuota 1:* {d[sel]['C1']}"
    st.text_area("Copiá el texto:", msj)
    st.markdown(f"[📲 Enviar por WhatsApp](https://wa.me/?text={msj.replace(' ', '%20').replace('\n', '%0A')})")
else:
    st.info("👋 Hola Alejandro, subí una planilla para ver los precios.")

if st.sidebar.button("🗑️ Reset"):
    st.session_state.clear()
    st.rerun()
