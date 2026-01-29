import streamlit as st
import pandas as pd
import easyocr
import numpy as np
from PIL import Image
import re

st.set_page_config(page_title="Arias Hnos. | Lector Estable", layout="wide")
st.title("🚗 Arias Hnos. | Sistema de Precios")

@st.cache_resource
def get_reader():
    return easyocr.Reader(['es'])

reader = get_reader()

def limpiar_precio(texto, es_cuota=False):
    num = re.sub(r'[^0-9]', '', texto)
    if not num or len(num) < 5: return None
    
    # Si el número es muy largo (más de 7 dígitos), es el valor del auto, no la cuota [cite: 2026-01-27]
    if len(num) > 7: return None
    
    # Corrección del error del signo $ (quita el 5, 8 o 3 inicial si queda de 7 dígitos) [cite: 2026-01-27]
    if len(num) == 7 and num.startswith(('5', '8', '3')):
        num = num[1:]
    
    valor = int(num)
    
    # --- FILTRO DE SEGURIDAD PARA CUOTA 1 --- [cite: 2026-01-27]
    # Una cuota 1 real en Arias Hnos hoy está entre $300k y $1.5M.
    # Si detecta algo fuera de ese rango (como los $14.150 de la imagen), lo ignora.
    if es_cuota and (valor < 300000 or valor > 1500000):
        return None
        
    return f"${valor:,}".replace(",", ".")

# --- INTERFAZ --- [cite: 2026-01-27]
opcion = st.radio("¿Qué desea hacer?", ["Cargar planilla nueva", "Usar datos guardados"])

if opcion == "Cargar planilla nueva":
    archivo = st.file_uploader("Subí la planilla", type=['jpg', 'jpeg', 'png'])
    if archivo:
        with st.spinner('🤖 Procesando con filtros de seguridad...'):
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
                    if "SUSC" in t_up:
                        for j in range(1, 4):
                            if i+j < len(res):
                                p = limpiar_precio(res[i+j], es_cuota=False)
                                if p: 
                                    datos[mod_actual]["Susc"] = p
                                    break
                    
                    if "CUOTA" in t_up:
                        for j in range(1, 4):
                            if i+j < len(res):
                                # Aplicamos el filtro estricto de cuota aquí [cite: 2026-01-27]
                                p = limpiar_precio(res[i+j], es_cuota=True)
                                if p: 
                                    datos[mod_actual]["C1"] = p
                                    break

            st.session_state.memoria_arias = datos

# --- SALIDA --- [cite: 2026-01-28]
if 'memoria_arias' in st.session_state:
    d = st.session_state.memoria_arias
    df = pd.DataFrame([{"Modelo": m, "Suscripción": d[m]["Susc"], "Cuota 1": d[m]["C1"]} for m in d])
    st.table(df)
    
    # Botones de Copiado [cite: 2026-01-27]
    st.divider()
    sel = st.selectbox("Elegí el modelo:", list(d.keys()))
    msj = f"*Arias Hnos.*\n*Auto:* {sel}\n✅ *Suscripción:* {d[sel]['Susc']}\n✅ *Cuota 1:* {d[sel]['C1']}"
    st.text_area("Copiá desde acá:", msj)
    st.markdown(f"[📲 Enviar WhatsApp](https://wa.me/?text={msj.replace(' ', '%20').replace('\n', '%0A')})")

if st.sidebar.button("🗑️ Reset"):
    st.session_state.clear()
    st.rerun()
