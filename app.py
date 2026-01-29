import streamlit as st
import pandas as pd
import easyocr
import numpy as np
from PIL import Image
import re

st.set_page_config(page_title="Arias Hnos. | Sistema Estable", layout="wide")
st.title("🚗 Arias Hnos. | Lector de Planillas")

@st.cache_resource
def get_reader():
    return easyocr.Reader(['es'])

reader = get_reader()

def limpiar_precio(texto):
    # Solo números [cite: 2026-01-27]
    num = re.sub(r'[^0-9]', '', texto)
    # Si el número es muy largo (más de 7 dígitos), es el valor del auto, no la cuota
    if not num or len(num) < 5 or len(num) > 7:
        return None
    # Si empieza con 5 u 8 y es largo, corregimos el error del signo $ [cite: 2026-01-27]
    if len(num) == 7 and num.startswith(('5', '8', '3')):
        num = num[1:]
    return f"${int(num):,}".replace(",", ".")

# --- SISTEMA DE MEMORIA --- [cite: 2026-01-27]
if 'datos' not in st.session_state:
    st.session_state.datos = None

menu = st.radio("¿Qué desea hacer?", ["Cargar planilla nueva", "Usar datos guardados"])

if menu == "Cargar planilla nueva":
    archivo = st.file_uploader("Subí la foto aquí", type=['jpg', 'jpeg', 'png'])
    if archivo:
        with st.spinner('🤖 Leyendo datos...'):
            img = Image.open(archivo)
            res = reader.readtext(np.array(img), detail=0)
            
            modelos = ["TERA", "VIRTUS", "T-CROSS", "NIVUS", "AMAROK", "TAOS"]
            resultados = {m: {"Susc": "$0", "C1": "$0"} for m in modelos}
            
            mod_actual = None
            for i, texto in enumerate(res):
                t_up = texto.upper()
                # Detectar el modelo
                for m in modelos:
                    if m in t_up: mod_actual = m
                
                if mod_actual:
                    # Si encontramos la palabra clave, el precio está en los bloques siguientes
                    if "SUSC" in t_up:
                        for j in range(1, 4):
                            if i+j < len(res):
                                p = limpiar_precio(res[i+j])
                                if p: 
                                    resultados[mod_actual]["Susc"] = p
                                    break
                    
                    if "CUOTA" in t_up:
                        for j in range(1, 4):
                            if i+j < len(res):
                                p = limpiar_precio(res[i+j])
                                if p: 
                                    resultados[mod_actual]["C1"] = p
                                    break
            
            st.session_state.datos = resultados
            st.success("✅ ¡Leído con éxito!")

# --- MOSTRAR TABLA Y BOTONES --- [cite: 2026-01-28]
if st.session_state.datos:
    d = st.session_state.datos
    df = pd.DataFrame([{"Modelo": m, "Suscripción": d[m]["Susc"], "Cuota 1": d[m]["C1"]} for m in d])
    st.table(df)
    
    # Herramientas de envío [cite: 2026-01-27]
    st.divider()
    sel = st.selectbox("Seleccioná modelo para mensaje:", list(d.keys()))
    mensaje = f"*Arias Hnos.*\n*Auto:* {sel}\n✅ *Suscripción:* {d[sel]['Susc']}\n✅ *Cuota 1:* {d[sel]['C1']}"
    st.text_area("Copia este texto:", mensaje)
    st.markdown(f"[📲 Enviar por WhatsApp](https://wa.me/?text={mensaje.replace(' ', '%20').replace('\n', '%0A')})")

if st.sidebar.button("🗑️ Borrar Memoria"):
    st.session_state.clear()
    st.rerun()
