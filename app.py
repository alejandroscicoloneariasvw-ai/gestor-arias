import streamlit as st
import pandas as pd
import easyocr
import numpy as np
from PIL import Image
import re

st.set_page_config(page_title="Gestor Arias Hnos.", layout="wide")
st.title("🚗 Gestor Arias Hnos. | Versión Estable")

@st.cache_resource
def load_reader():
    return easyocr.Reader(['es'])

reader = load_reader()

def limpiar_precio(texto):
    # Esta es la limpieza simple que funcionaba en la imagen image_5f0d9f.png [cite: 2026-01-27]
    num = re.sub(r'[^0-9]', '', texto)
    if len(num) >= 7 and num.startswith(('5', '8', '3')):
        num = num[1:]
    return f"${int(num):,}".replace(",", ".") if num else "$0"

# --- INTERFAZ --- [cite: 2026-01-27]
opcion = st.radio("Menú:", ["Cargar nueva planilla", "Ver datos guardados"])

if opcion == "Cargar nueva planilla":
    archivo = st.file_uploader("Subir imagen", type=['jpg', 'jpeg', 'png'])
    if archivo:
        with st.spinner('Leyendo...'):
            img = Image.open(archivo)
            res = reader.readtext(np.array(img), detail=0)
            
            modelos = ["TERA", "VIRTUS", "T-CROSS", "NIVUS", "AMAROK", "TAOS"]
            datos = {m: {"Susc": "$0", "C1": "$0"} for m in modelos}
            
            mod_actual = None
            for i, texto in enumerate(res):
                t_up = texto.upper()
                for m in modelos:
                    if m in t_up: mod_actual = m
                
                if mod_actual:
                    # Lógica de posición pura (la que no fallaba) [cite: 2026-01-27]
                    if "SUSCRIP" in t_up and i+1 < len(res):
                        datos[mod_actual]["Susc"] = limpiar_precio(res[i+1])
                    if "CUOTA" in t_up and " 1" in t_up and i+1 < len(res):
                        datos[mod_actual]["C1"] = limpiar_precio(res[i+1])
            
            st.session_state.memoria = datos
            st.success("✅ ¡Lectura terminada!")

# --- MOSTRAR TABLA --- [cite: 2026-01-28]
if 'memoria' in st.session_state:
    d = st.session_state.memoria
    df = pd.DataFrame([{"Modelo": m, "Suscripción": d[m]["Susc"], "Cuota 1": d[m]["C1"]} for m in d])
    st.table(df)
    
    # Botones que pediste [cite: 2026-01-27]
    sel = st.selectbox("Seleccionar modelo:", list(d.keys()))
    msj = f"*Arias Hnos.*\n*Auto:* {sel}\n✅ *Suscripción:* {d[sel]['Susc']}\n✅ *Cuota 1:* {d[sel]['C1']}"
    st.text_area("Mensaje:", msj)
    st.markdown(f"[📩 Enviar WhatsApp](https://wa.me/?text={msj.replace(' ', '%20').replace('\n', '%0A')})")

if st.sidebar.button("♻️ Reiniciar"):
    st.session_state.clear()
    st.rerun()
