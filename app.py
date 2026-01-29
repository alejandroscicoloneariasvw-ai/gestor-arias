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

def extraer_precios_logicos(lista_texto):
    """Filtra solo los números que pueden ser cuotas de Arias Hnos."""
    precios = []
    for t in lista_texto:
        num = re.sub(r'[^0-9]', '', t)
        if 100000 < int(num or 0) < 3000000: # Rango: entre 100k y 3M
            # Limpieza del 5/8 inicial si el número quedó muy largo
            if len(num) == 7 and num.startswith(('5', '8', '3')):
                num = num[1:]
            precios.append(int(num))
    return precios

# --- MENÚ ---
opcion = st.radio("¿Qué desea hacer?", ["Cargar planilla nueva", "Usar datos guardados"])

if opcion == "Cargar planilla nueva":
    archivo = st.file_uploader("Subí la planilla", type=['jpg', 'jpeg', 'png'])
    if archivo:
        with st.spinner('🤖 Interpretando como humano...'):
            img = Image.open(archivo)
            # detail=1 nos da la posición en la hoja para no mezclar modelos
            res = reader.readtext(np.array(img)) 
            
            modelos = ["TERA", "VIRTUS", "T-CROSS", "NIVUS", "AMAROK", "TAOS"]
            datos = {m: {"Susc": "$0", "C1": "$0"} for m in modelos}
            
            for mod in modelos:
                encontrado = False
                for i, (bbox, texto, prob) in enumerate(res):
                    if mod in texto.upper():
                        # Buscamos los siguientes 15 bloques de texto cerca del modelo
                        bloques_cercanos = [r[1] for r in res[i+1 : i+15]]
                        precios = extraer_precios_logicos(bloques_cercanos)
                        
                        if len(precios) >= 2:
                            # El más alto suele ser la suscripción, el otro la cuota
                            susc = max(precios)
                            cuota = min(precios)
                            datos[mod]["Susc"] = f"${susc:,}".replace(",", ".")
                            datos[mod]["C1"] = f"${cuota:,}".replace(",", ".")
                            encontrado = True
                            break
            
            st.session_state.memoria_pro = datos
            st.success("✅ Planilla leída correctamente")

# --- INTERFAZ DE SALIDA ---
if 'memoria_pro' in st.session_state:
    d = st.session_state.memoria_pro
    df = pd.DataFrame([{"Modelo": m, "Suscripción": d[m]["Susc"], "Cuota 1": d[m]["C1"]} for m in modelos])
    st.table(df)

    st.divider()
    sel = st.selectbox("Seleccioná el modelo:", modelos)
    msg = f"*Arias Hnos.*\n*Vehículo:* {sel}\n✅ *Suscripción:* {d[sel]['Susc']}\n✅ *Cuota 1:* {d[sel]['C1']}"
    st.text_area("Mensaje listo:", msg)
    st.markdown(f"[📲 Enviar WhatsApp](https://wa.me/?text={msg.replace(' ', '%20').replace('\n', '%0A')})")

if st.sidebar.button("🗑️ Reset"):
    st.session_state.clear()
    st.rerun()
