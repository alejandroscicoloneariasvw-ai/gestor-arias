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
    # Filtro de longitud para evitar valores móviles de millones [cite: 2026-01-27]
    if not num or len(num) < 5 or len(num) > 7: 
        return None
    # Corrección del error del signo $ [cite: 2026-01-27]
    if len(num) == 7 and num.startswith(('5', '8', '3')):
        num = num[1:]
    return int(num)

# --- INTERFAZ --- [cite: 2026-01-27]
opcion = st.radio("Acción:", ["Cargar nueva planilla", "Usar datos guardados"])

if opcion == "Cargar nueva planilla":
    archivo = st.file_uploader("Subí la planilla", type=['jpg', 'jpeg', 'png'])
    if archivo:
        with st.spinner('🤖 Identificando montos diferentes...'):
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
                    # BUSCAR SUSCRIPCIÓN (Primer monto que encuentre)
                    if "SUSC" in t_up and datos[mod_actual]["Susc"] == 0:
                        for j in range(1, 4):
                            if i+j < len(res):
                                p = limpiar_precio(res[i+j])
                                if p:
                                    datos[mod_actual]["Susc"] = p
                                    break
                    
                    # BUSCAR CUOTA 1 (El SEGUNDO monto válido después de la palabra clave) [cite: 2026-01-27]
                    if "CUOTA" in t_up and "12" not in t_up and "84" not in t_up:
                        if datos[mod_actual]["C1"] == 0:
                            encontrados = []
                            # Miramos más adelante (hasta 6 bloques) para captar la Cuota 1 real
                            for j in range(1, 6):
                                if i+j < len(res):
                                    p = limpiar_precio(res[i+j])
                                    if p: encontrados.append(p)
                            
                            # Si encontró al menos uno, el primero suele ser suscripción y el segundo la Cuota 1
                            if len(encontrados) >= 1:
                                # Usamos el último encontrado en el bloque cercano para asegurar que sea la cuota
                                datos[mod_actual]["C1"] = encontrados[-1]

            # Formatear para mostrar
            for m in datos:
                datos[m]["Susc"] = f"${datos[m]['Susc']:,}".replace(",", ".") if datos[m]["Susc"] > 0 else "$0"
                datos[m]["C1"] = f"${datos[m]['C1']:,}".replace(",", ".") if datos[m]["C1"] > 0 else "$0"

            st.session_state.memoria_arias = datos
            st.success("✅ ¡Planilla procesada!")

# --- SALIDA --- [cite: 2026-01-28]
if 'memoria_arias' in st.session_state:
    d = st.session_state.memoria_arias
    df = pd.DataFrame([{"Modelo": m, "Suscripción": d[m]["Susc"], "Cuota 1": d[m]["C1"]} for m in modelos])
    st.table(df)
    
    st.divider()
    sel = st.selectbox("Elegí modelo:", modelos)
    msj = f"*Arias Hnos.*\n*Auto:* {sel}\n✅ *Suscripción:* {d[sel]['Susc']}\n✅ *Cuota 1:* {d[sel]['C1']}"
    st.text_area("Mensaje:", msj)
    st.markdown(f"[📲 Enviar WhatsApp](https://wa.me/?text={msj.replace(' ', '%20').replace('\n', '%0A')})")

if st.sidebar.button("🗑️ Reset"):
    st.session_state.clear()
    st.rerun()
