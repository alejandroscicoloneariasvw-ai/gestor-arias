import streamlit as st
import pandas as pd
import easyocr
import numpy as np
from PIL import Image
import re

st.set_page_config(page_title="Arias Hnos. | Sistema Final", layout="wide")
st.title("?? Arias Hnos. | Lector de Planillas")

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

# --- MEMORIA Y SELECCIÓN ---
if 'memoria_final' not in st.session_state:
    st.session_state.memoria_final = None

opcion = st.radio("Menú Principal:", ["Cargar una planilla nueva", "Usar datos guardados"])

if opcion == "Cargar una planilla nueva":
    archivo = st.file_uploader("Subí la planilla (JPG/PNG)", type=['jpg', 'jpeg', 'png'])
    if archivo:
        with st.spinner('?? Procesando datos estables...'):
            img = Image.open(archivo)
            res = reader.readtext(np.array(img), detail=0)
            
            modelos = ["TERA", "VIRTUS", "T-CROSS", "NIVUS", "AMAROK", "TAOS"]
            datos = {m: {"Susc": 0, "C1": 0} for m in modelos}
            
            mod_actual = None
            for i, texto in enumerate(res):
                t_up = texto.upper()
                for m in modelos:
                    if m in t_up: mod_actual = m
                
                if mod_actual:
                    # SUSCRIPCIÓN (Toma el primer monto válido)
                    if "SUSC" in t_up and datos[mod_actual]["Susc"] == 0:
                        for j in range(1, 4):
                            if i+j < len(res):
                                p = limpiar_precio(res[i+j])
                                if p:
                                    datos[mod_actual]["Susc"] = p
                                    break
                    
                    # CUOTA 1 (Toma el segundo monto válido para evitar duplicados)
                    if "CUOTA" in t_up and "12" not in t_up and "84" not in t_up:
                        if datos[mod_actual]["C1"] == 0:
                            encontrados = []
                            for j in range(1, 6):
                                if i+j < len(res):
                                    p = limpiar_precio(res[i+j])
                                    if p: encontrados.append(p)
                            if len(encontrados) >= 1:
                                datos[mod_actual]["C1"] = encontrados[-1]

            # Formateo de salida
            final = {}
            for m in modelos:
                final[m] = {
                    "Susc": f"${datos[m]['Susc']:,}".replace(",", ".") if datos[m]["Susc"] > 0 else "$0",
                    "C1": f"${datos[m]['C1']:,}".replace(",", ".") if datos[m]["C1"] > 0 else "$0"
                }
            st.session_state.memoria_final = final
            st.success("? Lectura terminada con éxito.")

# --- RESULTADOS ---
if st.session_state.memoria_final:
    d = st.session_state.memoria_final
    df = pd.DataFrame([{"Modelo": m, "Suscripción": d[m]["Susc"], "Cuota 1": d[m]["C1"]} for m in d])
    st.table(df)
    
    st.divider()
    sel = st.selectbox("Seleccioná modelo para el mensaje:", list(d.keys()))
    msj = f"*Arias Hnos.*\n*Auto:* {sel}\n? *Suscripción:* {d[sel]['Susc']}\n? *Cuota 1:* {d[sel]['C1']}"
    st.text_area("Mensaje para copiar:", msj, height=100)
    
    link = f"https://wa.me/?text={msj.replace(' ', '%20').replace('\n', '%0A')}"
    st.markdown(f"[?? Enviar por WhatsApp]({link})")

if st.sidebar.button("??? Borrar Todo"):
    st.session_state.clear()
    st.rerun()
