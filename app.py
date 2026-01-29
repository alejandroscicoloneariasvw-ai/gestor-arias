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

def limpiar_precio_estricto(texto):
    num = re.sub(r'[^0-9]', '', texto)
    if len(num) < 5 or len(num) > 8: return None # Filtra números basura o muy largos
    if num.startswith(('5', '8', '3')) and len(num) >= 7: num = num[1:]
    return f"${int(num):,}".replace(",", ".")

archivo = st.file_uploader("Subí la planilla", type=['jpg', 'jpeg', 'png'])

if archivo:
    st.image(archivo, width=350, caption="Planilla detectada")
    
    with st.spinner('🤖 Extrayendo precios con precisión...'):
        img = Image.open(archivo)
        res = reader.readtext(np.array(img), detail=0)
        
        modelos = ["TERA", "VIRTUS", "T-CROSS", "NIVUS", "AMAROK", "TAOS"]
        datos_foto = {m: {"Susc": "$0", "C1": "$0"} for m in modelos}
        
        if res:
            mod_foco = None
            for i, texto in enumerate(res):
                t_up = texto.upper()
                
                # Detectar Modelo
                for mod in modelos:
                    if mod in t_up: mod_foco = mod
                
                if mod_foco:
                    # BUSCAR SUSCRIPCIÓN (Más rango para hojas de colores) [cite: 2026-01-27]
                    if any(x in t_up for x in ["SUSC", "SCRIP", "SU5C"]):
                        for k in range(1, 5):
                            if i+k < len(res):
                                p = limpiar_precio_estricto(res[i+k])
                                if p:
                                    datos_foto[mod_foco]["Susc"] = p
                                    break
                    
                    # BUSCAR CUOTA 1 (Solo el primer valor después de 'Cuota 1') [cite: 2026-01-28]
                    if "CUOTA" in t_up and "1" in t_up:
                        for k in range(1, 4):
                            if i+k < len(res):
                                p = limpiar_precio_estricto(res[i+k])
                                if p:
                                    datos_foto[mod_foco]["C1"] = p
                                    break # Corta enseguida para no agarrar la cuota 14-84
            
            df = pd.DataFrame([
                {"Modelo": m, "Suscripción": datos_foto[m]["Susc"], "Cuota 1": datos_foto[m]["C1"]}
                for m in modelos
            ])
            
            st.subheader("📊 Tabla de Precios")
            st.table(df)

            # --- GENERADOR DE MENSAJE WHATSAPP --- [cite: 2026-01-27, 2026-01-28]
            st.divider()
            st.subheader("📲 Generar Mensaje")
            seleccion = st.selectbox("Elegí el modelo para enviar:", modelos)
            
            p_susc = datos_foto[seleccion]["Susc"]
            p_c1 = datos_foto[seleccion]["C1"]
            
            mensaje = f"*Arias Hnos. | Detalle para el:*\n*Vehículo:* {seleccion}\n\n*Inversión Inicial:*\n✅ *Suscripción:* {p_susc}\n✅ *Cuota Nº 1:* {p_c1}"
            
            st.text_area("Copia este texto:", mensaje, height=150)
            
            # Botones de acción
            col1, col2 = st.columns(2)
            with col1:
                st.button("📋 Copiar Mensaje (Usar Ctrl+C)")
            with col2:
                # Link directo a WhatsApp Web
                link = f"https://wa.me/?text={mensaje.replace(' ', '%20').replace('\n', '%0A')}"
                st.markdown(f"[📩 Enviar por WhatsApp]({link})")

if st.sidebar.button("♻️ Reiniciar Sistema"):
    st.cache_resource.clear()
    st.rerun()
