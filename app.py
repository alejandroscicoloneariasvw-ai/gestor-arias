import streamlit as st
import pandas as pd
import easyocr
import numpy as np
from PIL import Image
import re

st.set_page_config(page_title="Arias Hnos. | Lector Pro", layout="wide")
st.title("🚗 Arias Hnos. | Lector de Planillas")

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

opcion = st.radio("Menú Principal:", ["Cargar una planilla nueva", "Usar datos guardados"])

if opcion == "Cargar una planilla nueva":
    archivo = st.file_uploader("Subí la planilla amarilla", type=['jpg', 'jpeg', 'png'])
    if archivo:
        with st.spinner('🚀 Vinculando montos por palabra clave...'):
            img = Image.open(archivo)
            res = reader.readtext(np.array(img), detail=0)
            
            modelos = ["TERA", "VIRTUS", "T-CROSS", "NIVUS", "AMAROK", "TAOS"]
            datos = {m: {"Susc": 0, "C1": 0, "C2_13": 0, "C14_84": 0} for m in modelos}
            
            mod_actual = None
            for i, texto in enumerate(res):
                t_up = texto.upper()
                for m in modelos:
                    if m in t_up: mod_actual = m
                
                if mod_actual:
                    # 1. SUSCRIPCIÓN
                    if "SUSC" in t_up and datos[mod_actual]["Susc"] == 0:
                        for j in range(1, 4):
                            if i+j < len(res):
                                p = limpiar_precio(res[i+j])
                                if p:
                                    datos[mod_actual]["Susc"] = p
                                    break
                    
                    # 2. CUOTA 1 (El monto que suele estar cerca de la palabra CUOTA)
                    if "CUOTA" in t_up and "12" not in t_up and "84" not in t_up:
                        if datos[mod_actual]["C1"] == 0:
                            for j in range(1, 5):
                                if i+j < len(res):
                                    p = limpiar_precio(res[i+j])
                                    if p and p != datos[mod_actual]["Susc"]:
                                        datos[mod_actual]["C1"] = p
                                        break

                    # 3. CUOTA 2-13 (Usamos tu hallazgo: la palabra ADHERIDO)
                    if "ADHERI" in t_up and datos[mod_actual]["C2_13"] == 0:
                        for j in range(1, 4):
                            if i+j < len(res):
                                p = limpiar_precio(res[i+j])
                                if p:
                                    datos[mod_actual]["C2_13"] = p
                                    break

                    # 4. CUOTA 14-84 (Buscamos el monto restante que sea menor a la C1)
                    if datos[mod_actual]["C14_84"] == 0 and datos[mod_actual]["C1"] > 0:
                        for j in range(1, 15):
                            if i+j < len(res):
                                p = limpiar_precio(res[i+j])
                                # Si encontramos un precio que no es ninguno de los anteriores
                                if p and p not in [datos[mod_actual]["Susc"], datos[mod_actual]["C1"], datos[mod_actual]["C2_13"]]:
                                    if p > 100000: # Filtro de seguridad
                                        datos[mod_actual]["C14_84"] = p
                                        break

            st.session_state.memoria_final = {m: {
                "Susc": f"${datos[m]['Susc']:,}".replace(",", ".") if datos[m]["Susc"] > 0 else "$0",
                "C1": f"${datos[m]['C1']:,}".replace(",", ".") if datos[m]["C1"] > 0 else "$0",
                "C2_13": f"${datos[m]['C2_13']:,}".replace(",", ".") if datos[m]["C2_13"] > 0 else "$0",
                "C14_84": f"${datos[m]['C14_84']:,}".replace(",", ".") if datos[m]["C14_84"] > 0 else "$0"
            } for m in modelos}
            st.success("✅ ¡Vinculación por ADHERIDO exitosa!")

# --- VISTA ---
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
    st.text_area("Copiá el texto:", msj, height=150)
    st.markdown(f"[📲 Enviar por WhatsApp](https://wa.me/?text={msj.replace(' ', '%20').replace('\n', '%0A')})")

if st.sidebar.button("🗑️ Reset"):
    st.session_state.clear()
    st.rerun()
