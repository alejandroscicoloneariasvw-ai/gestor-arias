import streamlit as st
import pandas as pd
import easyocr
import numpy as np
from PIL import Image
import re

st.set_page_config(page_title="Arias Hnos. | Lector Pro", layout="wide")
st.title("🚗 Arias Hnos. | Sistema de Precios")

@st.cache_resource
def get_reader():
    return easyocr.Reader(['es'])

reader = get_reader()

def limpiar_precio(texto):
    # Solo dejamos números [cite: 2026-01-27]
    num = re.sub(r'[^0-9]', '', texto)
    # Filtro de seguridad: una cuota real tiene entre 6 y 7 dígitos ($490.000)
    # Si tiene 8 o más, es el valor del auto y lo descartamos [cite: 2026-01-27]
    if not num or len(num) < 5 or len(num) > 7: 
        return None
    # Limpieza del 5 u 8 rebelde del principio [cite: 2026-01-27]
    if len(num) == 7 and num.startswith(('5', '8', '3')):
        num = num[1:]
    return f"${int(num):,}".replace(",", ".")

# --- MENÚ DE INICIO --- [cite: 2026-01-27]
opcion = st.radio("¿Qué desea hacer?", ["Cargar una planilla nueva", "Usar datos guardados"])

if opcion == "Cargar una planilla nueva":
    archivo = st.file_uploader("Subí la planilla", type=['jpg', 'jpeg', 'png'])
    if archivo:
        with st.spinner('🤖 Procesando datos...'):
            img = Image.open(archivo)
            res = reader.readtext(np.array(img), detail=0)
            
            modelos = ["TERA", "VIRTUS", "T-CROSS", "NIVUS", "AMAROK", "TAOS"]
            datos = {m: {"Susc": "$0", "C1": "$0"} for m in modelos}
            
            modelo_actual = None
            for i, texto in enumerate(res):
                t_up = texto.upper()
                
                for mod in modelos:
                    if mod in t_up: modelo_actual = mod
                
                if modelo_actual:
                    # Buscamos en los siguientes 2 bloques de texto para mayor precisión [cite: 2026-01-27]
                    if "SUSC" in t_up:
                        for j in [1, 2]:
                            if i+j < len(res):
                                p = limpiar_precio(res[i+j])
                                if p: 
                                    datos[modelo_actual]["Susc"] = p
                                    break
                    
                    if "CUOTA" in t_up:
                        for j in [1, 2]:
                            if i+j < len(res):
                                p = limpiar_precio(res[i+j])
                                if p: 
                                    datos[modelo_actual]["C1"] = p
                                    break

            st.session_state.datos_arias = datos
            st.success("✅ ¡Lectura terminada!")

# --- MOSTRAR RESULTADOS --- [cite: 2026-01-27, 2026-01-28]
if 'datos_arias' in st.session_state:
    d = st.session_state.datos_arias
    df = pd.DataFrame([{"Modelo": m, "Suscripción": d[m]["Susc"], "Cuota 1": d[m]["C1"]} for m in d])
    st.table(df)

    # Botones de Copia y WhatsApp [cite: 2026-01-27]
    st.divider()
    sel = st.selectbox("Elegí el modelo:", list(d.keys()))
    mensaje = f"*Arias Hnos.*\n*Auto:* {sel}\n✅ *Suscripción:* {d[sel]['Susc']}\n✅ *Cuota 1:* {d[sel]['C1']}"
    st.text_area("Copiá desde acá:", mensaje)
    st.markdown(f"[📲 Enviar por WhatsApp](https://wa.me/?text={mensaje.replace(' ', '%20').replace('\n', '%0A')})")

if st.sidebar.button("🗑️ LIMPIAR TODO"):
    st.session_state.clear()
    st.rerun()
