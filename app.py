import streamlit as st
import pandas as pd
import easyocr
import numpy as np
from PIL import Image
import re

st.set_page_config(page_title="Gestor Arias Hnos.", layout="wide")

# Función simple de limpieza (la que funcionaba al principio)
def limpiar_precio(texto):
    num = re.sub(r'[^0-9]', '', texto)
    if not num or len(num) < 5: return None
    # Si detecta un 5 u 8 extra al principio por el signo $ [cite: 2026-01-27]
    if len(num) >= 7 and num.startswith(('5', '8', '3')):
        num = num[1:]
    return f"${int(num):,}".replace(",", ".")

# --- INICIO DEL PROGRAMA --- [cite: 2026-01-27]
st.title(f"🚗 Gestor de Precios | Hola Alejandro")

# 1. Preguntar si cargar nueva o usar guardados
opcion = st.radio("Seleccione una opción:", ["Cargar una planilla nueva", "Usar datos guardados"], index=0)

if opcion == "Cargar una planilla nueva":
    archivo = st.file_uploader("Subí la foto de la planilla", type=['jpg', 'jpeg', 'png'])
    
    if archivo:
        with st.spinner('🤖 Leyendo planilla...'):
            reader = easyocr.Reader(['es'])
            img = Image.open(archivo)
            res = reader.readtext(np.array(img), detail=0)
            
            modelos = ["TERA", "VIRTUS", "T-CROSS", "NIVUS", "AMAROK", "TAOS"]
            datos = {m: {"Susc": "$0", "C1": "$0"} for m in modelos}
            
            mod_foco = None
            for i, texto in enumerate(res):
                t_up = texto.upper()
                for m in modelos:
                    if m in t_up: mod_foco = m
                
                if mod_foco:
                    # Buscamos el precio en un rango pequeño para que no se pierda (3 renglones)
                    if "SUSCRIP" in t_up:
                        for k in range(1, 4):
                            if i+k < len(res):
                                p = limpiar_precio(res[i+k])
                                if p: 
                                    datos[mod_foco]["Susc"] = p
                                    break
                    
                    if "CUOTA N" in t_up and " 1" in t_up:
                        for k in range(1, 4):
                            if i+k < len(res):
                                p = limpiar_precio(res[i+k])
                                if p:
                                    datos[mod_foco]["C1"] = p
                                    break
            
            st.session_state.guardado = datos
            st.success("✅ Datos leídos y guardados en memoria.")

# --- MOSTRAR RESULTADOS --- [cite: 2026-01-27, 2026-01-28]
if 'guardado' in st.session_state:
    df = pd.DataFrame([
        {"Modelo": m, "Suscripción": st.session_state.guardado[m]["Susc"], "Cuota 1": st.session_state.guardado[m]["C1"]}
        for m in st.session_state.guardado
    ])
    
    st.subheader("📊 Tabla de Precios")
    st.table(df)

    # --- BOTONES DE COPIA Y WHATSAPP --- [cite: 2026-01-27]
    st.divider()
    sel = st.selectbox("Seleccioná modelo para el mensaje:", list(st.session_state.guardado.keys()))
    
    msg = f"*Arias Hnos.*\n*Modelo:* {sel}\n✅ *Suscripción:* {st.session_state.guardado[sel]['Susc']}\n✅ *Cuota 1:* {st.session_state.guardado[sel]['C1']}"
    
    st.text_area("Mensaje para copiar:", msg)
    
    col1, col2 = st.columns(2)
    with col1:
        st.button("📋 Copiar (Seleccioná y Ctrl+C)")
    with col2:
        link = f"https://wa.me/?text={msg.replace(' ', '%20').replace('\n', '%0A')}"
        st.markdown(f"[📲 Enviar a WhatsApp]({link})")

else:
    st.info("No hay datos en memoria. Cargá una planilla para empezar.")

# Botón de reset [cite: 2026-01-27]
if st.sidebar.button("🗑️ Borrar todo"):
    st.session_state.clear()
    st.rerun()
