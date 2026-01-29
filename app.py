import streamlit as st
import pandas as pd
import easyocr
import numpy as np
from PIL import Image
import re

st.set_page_config(page_title="Arias Hnos. | Sistema Estable", layout="wide")
st.title("🚗 Arias Hnos. | Gestión de Precios")

@st.cache_resource
def get_reader():
    return easyocr.Reader(['es'])

reader = get_reader()

def limpiar_precio(texto):
    num = re.sub(r'[^0-9]', '', texto)
    if not num or len(num) < 5 or len(num) > 7: 
        return None
    if len(num) == 7 and num.startswith(('5', '8', '3')):
        num = num[1:]
    return int(num)

if 'memoria_final' not in st.session_state:
    st.session_state.memoria_final = None

opcion = st.radio("¿Qué desea hacer?", ["Cargar planilla nueva", "Usar datos guardados"])

if opcion == "Cargar planilla nueva":
    archivo = st.file_uploader("Subí la planilla", type=['jpg', 'jpeg', 'png'])
    if archivo:
        with st.spinner('🤖 Analizando datos...'):
            img = Image.open(archivo)
            res = reader.readtext(np.array(img), detail=0)
            modelos = ["TERA", "VIRTUS", "T-CROSS", "NIVUS", "AMAROK", "TAOS"]
            datos = {m: {"Susc": 0, "C1": 0} for m in modelos}
            
            for i, texto in enumerate(res):
                t_up = texto.upper()
                for m in modelos:
                    if m in t_up:
                        encontrados = []
                        for j in range(1, 15):
                            if i + j < len(res):
                                p = limpiar_precio(res[i+j])
                                if p: encontrados.append(p)
                        if len(encontrados) >= 2:
                            datos[m]["Susc"], datos[m]["C1"] = encontrados[0], encontrados[1]
                        elif len(encontrados) == 1:
                            datos[m]["C1"] = encontrados[0]

            st.session_state.memoria_final = {m: {
                "Susc": f"${datos[m]['Susc']:,}".replace(",", ".") if datos[m]["Susc"] > 0 else "$0",
                "C1": f"${datos[m]['C1']:,}".replace(",", ".") if datos[m]["C1"] > 0 else "$0"
            } for m in modelos}
            st.success("✅ Datos cargados correctamente.")

if st.session_state.memoria_final:
    d = st.session_state.memoria_final
    df = pd.DataFrame([{"Modelo": m, "Suscripción": d[m]["Susc"], "Cuota 1": d[m]["C1"]} for m in d])
    st.table(df)
    st.divider()
    sel = st.selectbox("Elegí el modelo:", list(d.keys()))
    msj = f"*Arias Hnos.*\n*Auto:* {sel}\n✅ *Suscripción:* {d[sel]['Susc']}\n✅ *Cuota 1:* {d[sel]['C1']}"
    st.text_area("Mensaje:", msj)
    st.markdown(f"[📲 Enviar WhatsApp](https://wa.me/?text={msj.replace(' ', '%20').replace('\n', '%0A')})")
else:
    st.info("👋 Hola Alejandro, cargá una planilla para ver los resultados.")

if st.sidebar.button("🗑️ Reset"):
    st.session_state.clear()
    st.rerun()
