import streamlit as st
import pandas as pd
import easyocr
import numpy as np
from PIL import Image
import re

st.set_page_config(page_title="Arias Hnos. | Lector Pro", layout="wide")
st.title("🚗 Arias Hnos. | Planilla de Cuotas Completa")

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

opcion = st.radio("Menú:", ["Cargar planilla nueva", "Usar datos guardados"])

if opcion == "Cargar planilla nueva":
    archivo = st.file_uploader("Subí la planilla (Amarilla)", type=['jpg', 'jpeg', 'png'])
    if archivo:
        with st.spinner('🤖 Analizando todas las cuotas...'):
            img = Image.open(archivo)
            res = reader.readtext(np.array(img), detail=0)
            
            modelos = ["TERA", "VIRTUS", "T-CROSS", "NIVUS", "AMAROK", "TAOS"]
            # Agregamos los nuevos campos a la estructura
            datos = {m: {"Susc": 0, "C1": 0, "C2_13": 0, "C14_84": 0} for m in modelos}
            
            mod_actual = None
            for i, texto in enumerate(res):
                t_up = texto.upper()
                for m in modelos:
                    if m in t_up: mod_actual = m
                
                if mod_actual:
                    # Buscamos todos los montos válidos cerca del modelo
                    encontrados = []
                    for j in range(1, 15):
                        if i + j < len(res):
                            p = limpiar_precio(res[i+j])
                            if p and p not in encontrados:
                                encontrados.append(p)
                    
                    # Asignamos en orden según aparecen en la planilla amarilla
                    if len(encontrados) >= 4:
                        datos[mod_actual]["Susc"] = encontrados[0]
                        datos[mod_actual]["C1"] = encontrados[1]
                        datos[mod_actual]["C2_13"] = encontrados[2]
                        datos[mod_actual]["C14_84"] = encontrados[3]

            # Formateo para la vista
            st.session_state.memoria_final = {m: {
                "Susc": f"${datos[m]['Susc']:,}".replace(",", ".") if datos[m]["Susc"] > 0 else "$0",
                "C1": f"${datos[m]['C1']:,}".replace(",", ".") if datos[m]["C1"] > 0 else "$0",
                "C2_13": f"${datos[m]['C2_13']:,}".replace(",", ".") if datos[m]["C2_13"] > 0 else "$0",
                "C14_84": f"${datos[m]['C14_84']:,}".replace(",", ".") if datos[m]["C14_84"] > 0 else "$0"
            } for m in modelos}
            st.success("✅ ¡Planilla completa procesada!")

# --- RESULTADOS ---
if st.session_state.memoria_final:
    d = st.session_state.memoria_final
    modelos_lista = ["TERA", "VIRTUS", "T-CROSS", "NIVUS", "AMAROK", "TAOS"]
    
    # Tabla con todas las columnas nuevas
    df_data = []
    for m in modelos_lista:
        df_data.append({
            "Modelo": m, 
            "Suscripción": d[m]["Susc"], 
            "Cuota 1": d[m]["C1"],
            "Cuotas 2-13": d[m]["C2_13"],
            "Cuotas 14-84": d[m]["C14_84"]
        })
    st.table(pd.DataFrame(df_data))
    
    st.divider()
    sel = st.selectbox("Elegí el modelo para el mensaje:", modelos_lista)
    
    # Mensaje de WhatsApp ampliado
    msj = (f"*Arias Hnos.*\n"
           f"*Auto:* {sel}\n"
           f"✅ *Suscripción:* {d[sel]['Susc']}\n"
           f"✅ *Cuota 1:* {d[sel]['C1']}\n"
           f"✅ *Cuotas 2 a 13:* {d[sel]['C2_13']}\n"
           f"✅ *Cuotas 14 a 84:* {d[sel]['C14_84']}")
           
    st.text_area("Copiá el presupuesto completo:", msj, height=150)
    st.markdown(f"[📲 Enviar por WhatsApp](https://wa.me/?text={msj.replace(' ', '%20').replace('\n', '%0A')})")
else:
    st.info("👋 Hola Alejandro, subí la planilla para generar el presupuesto completo.")

if st.sidebar.button("🗑️ Reset"):
    st.session_state.clear()
    st.rerun()
