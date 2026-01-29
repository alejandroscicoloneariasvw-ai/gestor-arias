import streamlit as st
import pandas as pd
import easyocr
import numpy as np
from PIL import Image
import re

st.set_page_config(page_title="Gestor Arias Hnos.", page_icon="🚗")
st.title("🚗 Arias Hnos. | Lector Pro")

@st.cache_resource
def cargar_lector():
    return easyocr.Reader(['es'])

reader = cargar_lector()

def limpiar_monto(texto):
    num = re.sub(r'[^0-9]', '', texto)
    if len(num) >= 7 and num.startswith(('5', '8', '3')):
        num = num[1:]
    return f"${int(num):,}".replace(",", ".") if num else "$0"

# --- INTERFAZ ---
# Te pregunta si cargar nueva o usar guardada como pediste [cite: 2026-01-27]
opcion = st.radio("¿Qué desea hacer?", ["Cargar una planilla nueva", "Usar datos guardados"])

if opcion == "Cargar una planilla nueva":
    archivo = st.file_uploader("Subí la foto de la planilla", type=['jpg', 'jpeg', 'png'])
    
    if archivo:
        st.image(archivo, width=250)
        with st.spinner('🤖 Procesando...'):
            img = Image.open(archivo)
            res = reader.readtext(np.array(img), detail=0)
            
            modelos = ["TERA", "VIRTUS", "T-CROSS", "NIVUS", "AMAROK", "TAOS"]
            datos = {m: {"Susc": "$0", "C1": "$0"} for m in modelos}
            
            mod_actual = None
            for i, texto in enumerate(res):
                t_up = texto.upper()
                for mod in modelos:
                    if mod in t_up: mod_actual = mod
                
                if mod_actual:
                    # Lógica original: precio en el renglón siguiente [cite: 2026-01-27]
                    if "SUSCRIP" in t_up and i+1 < len(res):
                        datos[mod_actual]["Susc"] = limpiar_monto(res[i+1])
                    if "CUOTA N" in t_up and " 1" in t_up and i+1 < len(res):
                        datos[mod_actual]["C1"] = limpiar_monto(res[i+1])
            
            st.session_state.viejos = datos
            st.success("✅ ¡Leído con éxito!")

# --- MOSTRAR TABLA ---
if 'viejos' in st.session_state:
    d = st.session_state.viejos
    df = pd.DataFrame([{"Modelo": m, "Suscripción": d[m]["Susc"], "Cuota 1": d[m]["C1"]} for m in modelos])
    st.subheader("📊 Tabla de Precios")
    st.table(df)
    
    # Botón de Copiar y WhatsApp [cite: 2026-01-27]
    st.divider()
    sel = st.selectbox("Elegí el modelo:", modelos)
    mensaje = f"*Arias Hnos.*\n*Modelo:* {sel}\n✅ *Suscripción:* {d[sel]['Susc']}\n✅ *Cuota 1:* {d[sel]['C1']}"
    st.text_area("Mensaje para copiar:", mensaje)
    st.markdown(f"[📲 Enviar por WhatsApp](https://wa.me/?text={mensaje.replace(' ', '%20').replace('\n', '%0A')})")

if st.sidebar.button("🗑️ Borrar Memoria"):
    st.session_state.clear()
    st.rerun()
