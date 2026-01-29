import streamlit as st
import pandas as pd
import easyocr
import numpy as np
from PIL import Image
import re

st.set_page_config(page_title="Arias Hnos. | Lector Pro")
st.title("🚗 Arias Hnos. | Sistema de Precios")

@st.cache_resource
def get_reader():
    return easyocr.Reader(['es'])

reader = get_reader()

def limpiar_precio(texto):
    num = re.sub(r'[^0-9]', '', texto)
    if num and len(num) >= 5:
        # Solo quita el 5 u 8 si el número es muy largo (signo $ mal leído) [cite: 2026-01-27]
        if len(num) >= 7 and num.startswith(('5', '8', '3')):
            num = num[1:]
        return f"${int(num):,}".replace(",", ".")
    return "$0"

# --- INTERFAZ SOLICITADA --- [cite: 2026-01-27]
opcion = st.radio("¿Qué desea hacer?", ["Cargar planilla nueva", "Usar datos guardados"])

if opcion == "Cargar planilla nueva":
    archivo = st.file_uploader("Subí la foto", type=['jpg', 'jpeg', 'png'])
    if archivo:
        with st.spinner('🤖 Leyendo...'):
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
                    # Lógica original: precio en el bloque siguiente [cite: 2026-01-27]
                    if "SUSC" in t_up and i+1 < len(res):
                        datos[mod_actual]["Susc"] = limpiar_precio(res[i+1])
                    if "CUOTA" in t_up and i+1 < len(res):
                        datos[mod_actual]["C1"] = limpiar_precio(res[i+1])
            
            st.session_state.viejos_datos = datos

# --- MOSTRAR TABLA --- [cite: 2026-01-28]
if 'viejos_datos' in st.session_state:
    d = st.session_state.viejos_datos
    df = pd.DataFrame([{"Modelo": m, "Suscripción": d[m]["Susc"], "Cuota 1": d[m]["C1"]} for m in modelos])
    st.table(df)
    
    # Botón de Copiar y WhatsApp [cite: 2026-01-27]
    st.divider()
    sel = st.selectbox("Elegí el modelo:", modelos)
    mensaje = f"*Arias Hnos.*\n*Auto:* {sel}\n✅ *Suscripción:* {d[sel]['Susc']}\n✅ *Cuota 1:* {d[sel]['C1']}"
    st.text_area("Copiá desde acá:", mensaje)
    st.markdown(f"[📲 Enviar por WhatsApp](https://wa.me/?text={mensaje.replace(' ', '%20').replace('\n', '%0A')})")

if st.sidebar.button("🗑️ LIMPIAR"):
    st.session_state.clear()
    st.rerun()
