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
    num = re.sub(r'[^0-9]', '', texto)
    # Una cuota lógica está entre 5 y 7 dígitos ($300.000 a $1.500.000) [cite: 2026-01-27]
    if not num or len(num) < 5 or len(num) > 7: 
        return None
    # Corrección del signo $ mal leído [cite: 2026-01-27]
    if len(num) == 7 and num.startswith(('5', '8', '3')):
        num = num[1:]
    return f"${int(num):,}".replace(",", ".")

# --- INTERFAZ --- [cite: 2026-01-27]
opcion = st.radio("Seleccioná acción:", ["Cargar planilla nueva", "Usar datos guardados"])

if opcion == "Cargar planilla nueva":
    archivo = st.file_uploader("Subí la planilla", type=['jpg', 'jpeg', 'png'])
    if archivo:
        with st.spinner('🤖 Analizando cada modelo por separado...'):
            img = Image.open(archivo)
            res = reader.readtext(np.array(img), detail=0)
            
            modelos = ["TERA", "VIRTUS", "T-CROSS", "NIVUS", "AMAROK", "TAOS"]
            datos = {m: {"Susc": "$0", "C1": "$0"} for m in modelos}
            
            # Variables de control para no pisar datos
            mod_actual = None
            
            for i, texto in enumerate(res):
                t_up = texto.upper()
                
                # Detectamos el modelo y lo fijamos como "el que estamos leyendo ahora"
                for m in modelos:
                    if m in t_up:
                        mod_actual = m
                
                if mod_actual:
                    # Buscamos la suscripción de ESTE modelo (si aún no la tiene)
                    if "SUSC" in t_up and datos[mod_actual]["Susc"] == "$0":
                        for j in range(1, 4):
                            if i+j < len(res):
                                p = limpiar_precio(res[i+j])
                                if p:
                                    datos[mod_actual]["Susc"] = p
                                    break
                    
                    # Buscamos la Cuota 1 de ESTE modelo (si aún no la tiene) [cite: 2026-01-27]
                    # Solo buscamos si dice "CUOTA" y NO menciona las cuotas altas (12 a 84)
                    if "CUOTA" in t_up and "12" not in t_up and "84" not in t_up:
                        if datos[mod_actual]["C1"] == "$0":
                            for j in range(1, 4):
                                if i+j < len(res):
                                    p = limpiar_precio(res[i+j])
                                    if p:
                                        datos[mod_actual]["C1"] = p
                                        break

            st.session_state.memoria_arias = datos
            st.success("✅ Datos individuales cargados.")

# --- SALIDA DE DATOS --- [cite: 2026-01-28]
if 'memoria_arias' in st.session_state:
    d = st.session_state.memoria_arias
    df = pd.DataFrame([{"Modelo": m, "Suscripción": d[m]["Susc"], "Cuota 1": d[m]["C1"]} for m in modelos])
    st.table(df)
    
    st.divider()
    sel = st.selectbox("Elegí modelo para el mensaje:", modelos)
    msj = f"*Arias Hnos.*\n*Auto:* {sel}\n✅ *Suscripción:* {d[sel]['Susc']}\n✅ *Cuota 1:* {d[sel]['C1']}"
    st.text_area("Copiá el texto:", msj)
    st.markdown(f"[📲 Enviar por WhatsApp](https://wa.me/?text={msj.replace(' ', '%20').replace('\n', '%0A')})")

if st.sidebar.button("🗑️ Reset"):
    st.session_state.clear()
    st.rerun()
