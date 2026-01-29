import streamlit as st
import pandas as pd
import easyocr
import numpy as np
from PIL import Image, ImageOps, ImageEnhance
import re

# Configuración de página
st.set_page_config(page_title="Arias Hnos. | Lector Pro", layout="wide")
st.title("🚗 Arias Hnos. | Sistema de Precios")

@st.cache_resource
def get_reader():
    return easyocr.Reader(['es'])

reader = get_reader()

def pre_procesar_imagen(pil_img):
    """Limpia la imagen para que la IA lea mejor el texto blanco sobre fondo oscuro."""
    gris = ImageOps.grayscale(pil_img)
    # Invertimos colores para que el texto sea negro y el fondo blanco (ayuda mucho en la roja)
    invertida = ImageOps.invert(gris)
    realzador = ImageEnhance.Contrast(invertida)
    return realzador.enhance(2.0)

def limpiar_precio(texto):
    num = re.sub(r'[^0-9]', '', texto)
    if not num or len(num) < 5 or len(num) > 7: 
        return None
    if len(num) == 7 and num.startswith(('5', '8', '3')):
        num = num[1:]
    return int(num)

# Inicializar memoria segura para evitar el error rojo de inicio
if 'memoria_final' not in st.session_state:
    st.session_state.memoria_final = None

opcion = st.radio("Seleccioná acción:", ["Cargar una planilla nueva", "Usar datos guardados"])

if opcion == "Cargar una planilla nueva":
    archivo = st.file_uploader("Subí la planilla", type=['jpg', 'jpeg', 'png'])
    if archivo:
        img_original = Image.open(archivo)
        with st.spinner('🎨 Optimizando lectura de planilla...'):
            img_limpia = pre_procesar_imagen(img_original)
            st.image(img_limpia, caption="Vista de lectura mejorada", width=400) # Para que veas el cambio
            
            res = reader.readtext(np.array(img_limpia), detail=0)
            
            # Buscamos modelos de forma secuencial
            modelos = ["TERA", "VIRTUS", "T-CROSS", "NIVUS", "AMAROK", "TAOS"]
            datos = {m: {"Susc": 0, "C1": 0} for m in modelos}
            
            mod_actual = None
            for i, texto in enumerate(res):
                t_up = texto.upper()
                for m in modelos:
                    if m in t_up: mod_actual = m
                
                if mod_actual:
                    # Si ya tenemos los datos, no seguimos buscando para este auto [cite: 2026-01-27]
                    if datos[mod_actual]["Susc"] != 0 and datos[mod_actual]["C1"] != 0:
                        continue

                    # Búsqueda de Suscripción (Busca términos variados de la lista roja)
                    if any(x in t_up for x in ["SUSC", "CUOTA DE", "PLAN"]) and datos[mod_actual]["Susc"] == 0:
                        for j in range(1, 6):
                            if i+j < len(res):
                                p = limpiar_precio(res[i+j])
                                if p:
                                    datos[mod_actual]["Susc"] = p
                                    break
                    
                    # Búsqueda de Cuota 1 (Evitando las de 12 a 84) [cite: 2026-01-27]
                    if "CUOTA" in t_up and "12" not in t_up and "84" not in t_up:
                        if datos[mod_actual]["C1"] == 0:
                            for j in range(1, 8):
                                if i+j < len(res):
                                    p = limpiar_precio(res[i+j])
                                    if p and p != datos[mod_actual]["Susc"]:
                                        datos[mod_actual]["C1"] = p
                                        break

            # Formatear para la tabla final
            final = {m: {
                "Susc": f"${datos[m]['Susc']:,}".replace(",", ".") if datos[m]["Susc"] > 0 else "$0",
                "C1": f"${datos[m]['C1']:,}".replace(",", ".") if datos[m]["C1"] > 0 else "$0"
            } for m in modelos}
            st.session_state.memoria_final = final
            st.success("✅ Análisis completo.")

# --- RESULTADOS (Protección contra NameError) ---
if st.session_state.memoria_final is not None:
    d = st.session_state.memoria_final
    modelos_lista = ["TERA", "VIRTUS", "T-CROSS", "NIVUS", "AMAROK", "TAOS"]
    df = pd.DataFrame([{"Modelo": m, "Suscripción": d[m]["Susc"], "Cuota 1": d[m]["C1"]} for m in modelos_lista])
    st.table(df)
    
    st.divider()
    sel = st.selectbox("Elegí el modelo:", modelos_lista)
    msj = f"*Arias Hnos.*\n*Auto:* {sel}\n✅ *Suscripción:* {d[sel]['Susc']}\n✅ *Cuota 1:* {d[sel]['C1']}"
    st.text_area("Mensaje listo para copiar:", msj)
    st.markdown(f"[📲 Enviar por WhatsApp](https://wa.me/?text={msj.replace(' ', '%20').replace('\n', '%0A')})")
else:
    st.info("👋 Hola Alejandro. Por favor, cargá la foto de la planilla para mostrar los precios.")

if st.sidebar.button("🗑️ Resetear Memoria"):
    st.session_state.clear()
    st.rerun()
