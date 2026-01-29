import streamlit as st
import pandas as pd
import easyocr
import numpy as np
from PIL import Image
import re

st.set_page_config(page_title="Gestor Arias Hnos.", page_icon="🚗")
st.title("🚗 Arias Hnos. | Lector Instantáneo")

# Cargamos el lector una sola vez para que no sea lento
if 'reader' not in st.session_state:
    with st.spinner('Iniciando sistema...'):
        st.session_state.reader = easyocr.Reader(['es'])

def limpiar_monto(texto):
    num = re.sub(r'[^0-9.]', '', texto)
    if len(num) >= 7 and num.startswith(('5', '8', '3')):
        num = num[1:]
    return f"${num}" if num else "$0"

# --- INTERFAZ ---
archivo = st.file_uploader("Subí la planilla", type=['jpg', 'jpeg', 'png'])

if archivo:
    # 1. Mostrar la imagen inmediatamente
    st.image(archivo, width=250)
    
    # 2. PROCESAR SIEMPRE (Sin memoria vieja) [cite: 2026-01-27]
    with st.spinner('🤖 Leyendo datos actuales...'):
        img = Image.open(archivo)
        res = st.session_state.reader.readtext(np.array(img), detail=0)
        
        modelos = ["TERA", "VIRTUS", "T-CROSS", "NIVUS", "AMAROK", "TAOS"]
        resultados_dict = {m: {"Susc": "$0", "C1": "$0"} for m in modelos}
        
        if res:
            modelos_map = {"TERA": 0, "VIRTUS": 1, "T-CROSS": 2, "NIVUS": 3, "AMAROK": 4, "TAOS": 5}
            for i, texto in enumerate(res):
                t_up = texto.upper()
                for mod in modelos:
                    if mod in t_up:
                        # Buscamos datos para este modelo
                        for j in range(i+1, min(i+20, len(res))):
                            if "Suscrip" in res[j] and j+1 < len(res):
                                resultados_dict[mod]["Susc"] = limpiar_monto(res[j+1])
                            if "Cuota No" in res[j] and j+1 < len(res):
                                if "." in res[j+1] and len(res[j+1]) > 4:
                                    resultados_dict[mod]["C1"] = limpiar_monto(res[j+1])
                                    break
            
            # 3. CREAR Y MOSTRAR TABLA FINAL [cite: 2026-01-28]
            df_final = pd.DataFrame([
                {"Modelo": m, "Suscripción": resultados_dict[m]["Susc"], "Cuota 1": resultados_dict[m]["C1"]}
                for m in modelos
            ])
            
            st.subheader("📊 Datos de la foto actual:")
            st.table(df_final)
            st.success("✅ ¡Listo!")
        else:
            st.error("No se pudo leer la imagen.")

# Botón de limpieza absoluta por si acaso
if st.sidebar.button("♻️ Reiniciar App por completo"):
    st.session_state.clear()
    st.rerun()
