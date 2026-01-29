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
    if not num or len(num) < 5 or len(num) > 7: 
        return None
    # Corrección de errores comunes de OCR en los primeros dígitos [cite: 2026-01-27]
    if len(num) == 7 and num.startswith(('5', '8', '3')):
        num = num[1:]
    return int(num)

if 'memoria_final' not in st.session_state:
    st.session_state.memoria_final = None

opcion = st.radio("Acción:", ["Cargar planilla nueva", "Usar datos guardados"])

if opcion == "Cargar planilla nueva":
    archivo = st.file_uploader("Subí la planilla amarilla", type=['jpg', 'jpeg', 'png'])
    if archivo:
        with st.spinner('🤖 Extrayendo datos por posición...'):
            img = Image.open(archivo)
            res = reader.readtext(np.array(img), detail=0)
            
            modelos = ["TERA", "VIRTUS", "T-CROSS", "NIVUS", "AMAROK", "TAOS"]
            datos = {m: {"Susc": 0, "C1": 0, "C2_13": 0, "C14_84": 0} for m in modelos}
            
            for i, texto in enumerate(res):
                t_up = texto.upper()
                for m in modelos:
                    if m in t_up:
                        # Cuando encontramos el modelo, capturamos los siguientes 4 precios válidos [cite: 2026-01-29]
                        encontrados = []
                        for j in range(1, 20): # Buscamos en un rango amplio de la fila
                            if i + j < len(res):
                                p = limpiar_precio(res[i+j])
                                if p and p not in encontrados:
                                    encontrados.append(p)
                                if len(encontrados) == 4: break # Ya tenemos las 4 columnas
                        
                        if len(encontrados) == 4:
                            datos[m]["Susc"] = encontrados[0]
                            datos[m]["C1"] = encontrados[1]
                            datos[m]["C2_13"] = encontrados[2]
                            datos[m]["C14_84"] = encontrados[3]

            st.session_state.memoria_final = {m: {
                "Susc": f"${datos[m]['Susc']:,}".replace(",", ".") if datos[m]["Susc"] > 0 else "$0",
                "C1": f"${datos[m]['C1']:,}".replace(",", ".") if datos[m]["C1"] > 0 else "$0",
                "C2_13": f"${datos[m]['C2_13']:,}".replace(",", ".") if datos[m]["C2_13"] > 0 else "$0",
                "C14_84": f"${datos[m]['C14_84']:,}".replace(",", ".") if datos[m]["C14_84"] > 0 else "$0"
            } for m in modelos}
            st.success("✅ Datos procesados por orden de fila.")

# --- RESULTADOS ---
if st.session_state.memoria_final:
    d = st.session_state.memoria_final
    modelos_lista = ["TERA", "VIRTUS", "T-CROSS", "NIVUS", "AMAROK", "TAOS"]
    df_data = [{"Modelo": m, "Suscripción": d[m]["Susc"], "Cuota 1": d[m]["C1"], "C 2-13": d[m]["C2_13"], "C 14-84": d[m]["C14_84"]} for m in modelos_lista]
    st.table(pd.DataFrame(df_data))
    
    st.divider()
    sel = st.selectbox("Elegí el modelo:", modelos_lista)
    msj = (f"*Arias Hnos.*\n*Auto:* {sel}\n"
           f"✅ *Suscripción:* {d[sel]['Susc']}\n"
           f"✅ *Cuota 1:* {d[sel]['C1']}\n"
           f"✅ *Cuotas 2 a 13:* {d[sel]['C2_13']}\n"
           f"✅ *Cuotas 14 a 84:* {d[sel]['C14_84']}")
    st.text_area("Mensaje listo:", msj, height=150)
    st.markdown(f"[📲 Enviar por WhatsApp](https://wa.me/?text={msj.replace(' ', '%20').replace('\n', '%0A')})")

if st.sidebar.button("🗑️ Limpiar"):
    st.session_state.clear()
    st.rerun()
