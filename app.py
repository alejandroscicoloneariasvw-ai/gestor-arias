import streamlit as st
import pandas as pd
import easyocr
import numpy as np
from PIL import Image
import re

st.set_page_config(page_title="Gestor Arias Hnos.", page_icon="🚗")
st.title("🚗 Arias Hnos. | Lector de Planillas")

@st.cache_resource
def cargar_lector():
    return easyocr.Reader(['es'])

reader = cargar_lector()

# Función para limpiar los precios "sucios" (ej: 5800.000 -> $800.000) [cite: 2026-01-27]
def limpiar_monto(texto):
    solo_numeros = re.sub(r'[^0-9.]', '', texto)
    if solo_numeros.startswith(('5', '8', '3')) and len(solo_numeros) > 7:
        solo_numeros = solo_numeros[1:] # Quitamos el error del lector
    return f"${solo_numeros}"

if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame({
        "Modelo": ["TERA TREND", "VIRTUS", "T-CROSS", "NIVUS", "AMAROK", "TAOS"],
        "Suscripción": ["$0"]*6, "Cuota 1": ["$0"]*6, "Cuota Pura": ["$0"]*6, "Adj": ["Pactada"]*6
    })

archivo = st.file_uploader("Subí la planilla de Arias Hnos.", type=['jpg', 'jpeg', 'png'])

if archivo:
    img = Image.open(archivo)
    st.image(img, width=400)
    with st.spinner('🤖 Procesando renglones...'):
        res = reader.readtext(np.array(img), detail=0)
        # Diccionario de búsqueda basado en tus renglones [cite: 2026-01-27, 2026-01-28]
        modelos = {"TERA": 0, "VIRTUS": 1, "T-CROSS": 2, "NIVUS": 3, "AMAROK": 4, "TAOS": 5}
        
        for i, texto in enumerate(res):
            t_up = texto.upper()
            for mod, fila in modelos.items():
                if mod in t_up:
                    # Extraer Adjudicación del mismo renglón
                    if "(" in texto:
                        st.session_state.df.at[fila, "Adj"] = texto[texto.find("(")+1:texto.find(")")]
                    
                    # Buscar precios en los siguientes 15 renglones
                    for j in range(i+1, min(i+18, len(res))):
                        proximo = res[j]
                        if "Suscripción" in proximo or "Suscrip" in proximo:
                            st.session_state.df.at[fila, "Suscripción"] = limpiar_monto(res[j+1])
                        if "Cuota No" in proximo or "Cuota Nº" in proximo:
                            st.session_state.df.at[fila, "Cuota 1"] = limpiar_monto(res[j+1])
                        if "PURA:" in proximo.upper():
                            st.session_state.df.at[fila, "Cuota Pura"] = limpiar_monto(proximo.split(":")[-1])

st.table(st.session_state.df)

# --- WHATSAPP --- [cite: 2026-01-28]
st.subheader("📲 Generar Mensaje")
sel = st.selectbox("Seleccioná el modelo:", st.session_state.df["Modelo"])
d = st.session_state.df[st.session_state.df["Modelo"] == sel].iloc[0]

msj = f"""*Arias Hnos.* | Detalle para el:
*Vehículo:* {sel}
✅ *ADJUDICACIÓN:* {d['Adj']}

*Inversión Inicial:*
* *Suscripción:* {d['Suscripción']}
* *Cuota Nº 1:* {d['Cuota 1']}
* *Cuota Pura:* {d['Cuota Pura']}

-----------------------------------------------------------
🔥 *BENEFICIO EXCLUSIVO:* Abonando solo *$400.000, cubrís el INGRESO COMPLETO de Cuota 1 y Suscripción.*
-----------------------------------------------------------
Para avanzar, mándame foto de DNI!"""

st.text_area("Copiá para WhatsApp:", msj, height=250)
