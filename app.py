import streamlit as st
import pandas as pd
import easyocr
import numpy as np
from PIL import Image, ImageOps, ImageEnhance
import re

st.set_page_config(page_title="Arias Hnos. | Lector Pro", layout="wide")
st.title("🚗 Arias Hnos. | Sistema con Limpieza de Color")

@st.cache_resource
def get_reader():
    return easyocr.Reader(['es'])

reader = get_reader()

def pre_procesar_imagen(pil_img):
    """Convierte a Blanco y Negro y mejora el contraste para mejor lectura."""
    # Convertir a escala de grises
    gris = ImageOps.grayscale(pil_img)
    # Aumentar el contraste drásticamente
    realzador = ImageEnhance.Contrast(gris)
    limpia = realzador.enhance(2.0) 
    return limpia

def limpiar_precio(texto):
    num = re.sub(r'[^0-9]', '', texto)
    if not num or len(num) < 5 or len(num) > 7: 
        return None
    if len(num) == 7 and num.startswith(('5', '8', '3')):
        num = num[1:]
    return int(num)

if 'memoria_final' not in st.session_state:
    st.session_state.memoria_final = None

opcion = st.radio("Seleccioná acción:", ["Cargar una planilla nueva", "Usar datos guardados"])

if opcion == "Cargar una planilla nueva":
    archivo = st.file_uploader("Subí la planilla", type=['jpg', 'jpeg', 'png'])
    if archivo:
        img_original = Image.open(archivo)
        
        # APLICAMOS LA LIMPIEZA DE COLOR [cite: 2026-01-29]
        with st.spinner('🎨 Limpiando colores y mejorando texto...'):
            img_limpia = pre_procesar_imagen(img_original)
            # Mostramos la versión limpia para que veas cómo la ve la IA
            st.image(img_limpia, caption="Vista optimizada para la IA", width=300)
            
            res = reader.readtext(np.array(img_limpia), detail=0)
            
            modelos = ["TERA", "VIRTUS", "T-CROSS", "NIVUS", "AMAROK", "TAOS"]
            datos = {m: {"Susc": 0, "C1": 0} for m in modelos}
            
            mod_actual = None
            for i, texto in enumerate(res):
                t_up = texto.upper()
                for m in modelos:
                    if m in t_up: mod_actual = m
                
                if mod_actual:
                    if datos[mod_actual]["Susc"] != 0 and datos[mod_actual]["C1"] != 0:
                        continue

                    # Buscamos Suscripción
                    if ("SUSC" in t_up or "CUOTA DE" in t_up) and datos[mod_actual]["Susc"] == 0:
                        for j in range(1, 5):
                            if i+j < len(res):
                                p = limpiar_precio(res[i+j])
                                if p:
                                    datos[mod_actual]["Susc"] = p
                                    break
                    
                    # Buscamos Cuota 1
                    if "CUOTA" in t_up and "12" not in t_up and "84" not in t_up:
                        if datos[mod_actual]["C1"] == 0:
                            for j in range(1, 6):
                                if i+j < len(res):
                                    p = limpiar_precio(res[i+j])
                                    if p and p != datos[mod_actual]["Susc"]:
                                        datos[mod_actual]["C1"] = p
                                        break

            final = {}
            for m in modelos:
                final[m] = {
                    "Susc": f"${datos[m]['Susc']:,}".replace(",", ".") if datos[m]["Susc"] > 0 else "$0",
                    "C1": f"${datos[m]['C1']:,}".replace(",", ".") if datos[m]["C1"] > 0 else "$0"
                }
            st.session_state.memoria_final = final
            st.success("✅ ¡Procesado con éxito!")

# --- RESULTADOS ---
if st.session_state.memoria_final:
    d = st.session_state.memoria_final
    df = pd.DataFrame([{"Modelo": m, "Suscripción": d[m]["Susc"], "Cuota 1": d[m]["C1"]} for m in modelos])
    st.table(df)
    
    st.divider()
    sel = st.selectbox("Elegí el modelo:", modelos)
    msj = f"*Arias Hnos.*\n*Auto:* {sel}\n✅ *Suscripción:* {d[sel]['Susc']}\n✅ *Cuota 1:* {d[sel]['C1']}"
    st.text_area("Copiá el texto:", msj)
    st.markdown(f"[📲 Enviar por WhatsApp](https://wa.me/?text={msj.replace(' ', '%20').replace('\n', '%0A')})")

if st.sidebar.button("🗑️ Reset"):
    st.session_state.clear()
    st.rerun()
