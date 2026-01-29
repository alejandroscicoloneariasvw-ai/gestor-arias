import streamlit as st
import pandas as pd
import easyocr
import numpy as np
from PIL import Image
import re

st.set_page_config(page_title="Gestor Arias Hnos.", layout="wide")
st.title("🚗 Arias Hnos. | Sistema de Precios")

@st.cache_resource
def get_reader():
    return easyocr.Reader(['es'])

reader = get_reader()

def limpiar_precio(texto):
    # Solo dejamos números
    num = re.sub(r'[^0-9]', '', texto)
    if not num or len(num) < 5: return None
    # Quitamos el 5, 8 o 3 rebelde del principio si es necesario [cite: 2026-01-27]
    if len(num) >= 7 and num.startswith(('5', '8', '3')):
        num = num[1:]
    return f"${int(num):,}".replace(",", ".")

# --- PREGUNTA DE INICIO --- [cite: 2026-01-27]
opcion = st.radio("¿Qué desea hacer?", ["Cargar una planilla nueva", "Usar datos guardados"])

if opcion == "Cargar una planilla nueva":
    archivo = st.file_uploader("Subí la foto o PDF", type=['jpg', 'jpeg', 'png'])
    
    if archivo:
        img = Image.open(archivo)
        st.image(img, width=300)
        
        with st.spinner('🤖 Leyendo...'):
            res = reader.readtext(np.array(img), detail=0)
            
            modelos = ["TERA", "VIRTUS", "T-CROSS", "NIVUS", "AMAROK", "TAOS"]
            datos = {m: {"Susc": "$0", "C1": "$0"} for m in modelos}
            
            mod_actual = None
            for i, texto in enumerate(res):
                t_up = texto.upper()
                
                # Detectar Modelo
                for mod in modelos:
                    if mod in t_up: mod_actual = mod
                
                if mod_actual:
                    # BUSQUEDA ORIGINAL (La que no fallaba) [cite: 2026-01-27]
                    if "SUSC" in t_up and i+1 < len(res):
                        p = limpiar_precio(res[i+1])
                        if p: datos[mod_actual]["Susc"] = p
                    
                    if "CUOTA" in t_up and i+1 < len(res):
                        p = limpiar_precio(res[i+1])
                        if p: datos[mod_actual]["C1"] = p

            st.session_state.memoria_alejandro = datos
            st.success("✅ ¡Leído y Guardado!")

# --- MOSTRAR RESULTADOS --- [cite: 2026-01-28]
if 'memoria_alejandro' in st.session_state:
    d = st.session_state.memoria_alejandro
    df = pd.DataFrame([{"Modelo": m, "Suscripción": d[m]["Susc"], "Cuota 1": d[m]["C1"]} for m in modelos])
    
    st.subheader("📊 Tabla de Precios")
    st.table(df)

    # --- BOTONES PARA WHATSAPP --- [cite: 2026-01-27]
    st.divider()
    sel = st.selectbox("Elegí el modelo para el mensaje:", modelos)
    mensaje = f"*Arias Hnos.*\n*Auto:* {sel}\n✅ *Suscripción:* {d[sel]['Susc']}\n✅ *Cuota 1:* {d[sel]['C1']}"
    
    st.text_area("Copiá desde acá:", mensaje, height=120)
    
    # Botón directo [cite: 2026-01-27]
    link = f"https://wa.me/?text={mensaje.replace(' ', '%20').replace('\n', '%0A')}"
    st.markdown(f"[📩 ENVIAR POR WHATSAPP]({link})")

if st.sidebar.button("🗑️ LIMPIAR MEMORIA"):
    st.session_state.clear()
    st.rerun()
