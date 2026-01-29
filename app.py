import streamlit as st
import pandas as pd
import easyocr
import numpy as np
from PIL import Image
import re

st.set_page_config(page_title="Gestor Arias Hnos.", layout="wide")

# Función de limpieza original (la que funcionaba) [cite: 2026-01-27]
def limpiar_monto(texto):
    num = re.sub(r'[^0-9]', '', texto)
    if not num or len(num) < 5: return None
    # Elimina errores de lectura del signo $ (como 5, 8 o 3 al inicio) [cite: 2026-01-27]
    if len(num) >= 7 and num.startswith(('5', '8', '3')):
        num = num[1:]
    return f"${int(num):,}".replace(",", ".")

st.title("🚗 Arias Hnos. | Lector de Planillas")

# --- MENÚ DE OPCIONES --- [cite: 2026-01-27]
opcion = st.radio("¿Qué desea hacer?", ["Cargar una planilla nueva", "Usar datos guardados"])

if opcion == "Cargar una planilla nueva":
    archivo = st.file_uploader("Subí la foto aquí", type=['jpg', 'jpeg', 'png'])
    
    if archivo:
        with st.spinner('🤖 Leyendo datos...'):
            reader = easyocr.Reader(['es'])
            img = Image.open(archivo)
            res = reader.readtext(np.array(img), detail=0)
            
            modelos = ["TERA", "VIRTUS", "T-CROSS", "NIVUS", "AMAROK", "TAOS"]
            datos = {m: {"Susc": "$0", "C1": "$0"} for m in modelos}
            
            mod_actual = None
            for i, texto in enumerate(res):
                t_up = texto.upper()
                # Detectar el auto
                for m in modelos:
                    if m in t_up: mod_actual = m
                
                if mod_actual:
                    # Búsqueda de Suscripción (máximo 2 renglones de distancia)
                    if "SUSCRIP" in t_up:
                        for k in [1, 2]:
                            if i+k < len(res):
                                p = limpiar_monto(res[i+k])
                                if p: 
                                    datos[mod_actual]["Susc"] = p
                                    break
                    
                    # Búsqueda de Cuota 1
                    if "CUOTA" in t_up and "1" in t_up:
                        for k in [1, 2]:
                            if i+k < len(res):
                                p = limpiar_monto(res[i+k])
                                if p:
                                    datos[mod_actual]["C1"] = p
                                    break
            
            # Guardamos en la memoria del navegador [cite: 2026-01-27]
            st.session_state.memoria_arias = datos
            st.success("✅ Planilla procesada con éxito.")

# --- MOSTRAR RESULTADOS SI HAY DATOS --- [cite: 2026-01-27, 2026-01-28]
if 'memoria_arias' in st.session_state:
    datos_ver = st.session_state.memoria_arias
    df = pd.DataFrame([
        {"Modelo": m, "Suscripción": datos_ver[m]["Susc"], "Cuota 1": datos_ver[m]["C1"]}
        for m in datos_ver
    ])
    
    st.subheader("📊 Tabla de Precios Actual")
    st.table(df)

    # --- MENSAJE PARA WHATSAPP --- [cite: 2026-01-27]
    st.divider()
    sel = st.selectbox("Elegí un modelo para enviar:", list(datos_ver.keys()))
    mensaje = f"*Arias Hnos.*\n*Modelo:* {sel}\n✅ *Suscripción:* {datos_ver[sel]['Susc']}\n✅ *Cuota 1:* {datos_ver[sel]['C1']}"
    
    st.text_area("Copiá este texto:", mensaje, height=100)
    
    link = f"https://wa.me/?text={mensaje.replace(' ', '%20').replace('\n', '%0A')}"
    st.markdown(f"[📲 Enviar por WhatsApp]({link})")

elif opcion == "Usar datos guardados":
    st.warning("Aún no has cargado ninguna planilla hoy.")

if st.sidebar.button("🗑️ Borrar Memoria"):
    st.session_state.clear()
    st.rerun()
