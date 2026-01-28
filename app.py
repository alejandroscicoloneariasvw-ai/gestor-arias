import streamlit as st
import pandas as pd
import easyocr
import numpy as np
from PIL import Image

st.set_page_config(page_title="Gestor Arias Hnos.", page_icon="🚗")
st.title("🚗 Arias Hnos. | Lector & WhatsApp")

@st.cache_resource
def cargar_lector():
    return easyocr.Reader(['es'])

reader = cargar_lector()

if 'df_ventas' not in st.session_state:
    datos = {
        "Modelo": ["TERA TREND", "VIRTUS", "T-CROSS", "NIVUS", "TAOS", "AMAROK"],
        "Suscripción": ["$0", "$0", "$0", "$0", "$0", "$0"],
        "Cuota 1": ["$0", "$0", "$0", "$0", "$0", "$0"],
        "Cuota Pura": ["$0", "$0", "$0", "$0", "$0", "$0"]
    }
    st.session_state.df_ventas = pd.DataFrame(datos)

archivo = st.file_uploader("Subí la planilla para actualizar y enviar", type=['jpg', 'jpeg', 'png'])

if archivo:
    img = Image.open(archivo)
    with st.spinner('🤖 Leyendo planilla y preparando mensajes...'):
        img_np = np.array(img)
        resultados = reader.readtext(img_np)
        modelos_map = {"tera": 0, "virtus": 1, "t-cross": 2, "nivus": 3, "taos": 4, "amarok": 5}
        
        for i, (bbox, texto, prob) in enumerate(resultados):
            t_low = texto.lower()
            for nombre, fila in modelos_map.items():
                if nombre in t_low:
                    precios = []
                    for j in range(i+1, min(i+15, len(resultados))):
                        val = resultados[j][1].replace(" ", "")
                        if "." in val and any(c.isdigit() for c in val) and "alicuota" not in val.lower():
                            precios.append(val)
                    if len(precios) >= 3:
                        st.session_state.df_ventas.at[fila, "Suscripción"] = f"${precios[0]}"
                        st.session_state.df_ventas.at[fila, "Cuota 1"] = f"${precios[1]}"
                        st.session_state.df_ventas.at[fila, "Cuota Pura"] = f"${precios[2]}"

st.table(st.session_state.df_ventas)

# --- SECCIÓN WHATSAPP --- [cite: 2026-01-27]
st.subheader("📲 Generar Mensaje para Cliente")
modelo_sel = st.selectbox("Seleccioná el vehículo para el mensaje:", st.session_state.df_ventas["Modelo"])
fila_sel = st.session_state.df_ventas[st.session_state.df_ventas["Modelo"] == modelo_sel].iloc[0]

# El esquema que me pasaste [cite: 2026-01-28]
mensaje_wa = f"""Basada en la planilla de *Arias Hnos.*, aquí tienes el detalle para el:

*Vehículo:* {modelo_sel}
*Plazo:* 84 Cuotas (Pre-cancelables a Cuota Pura de *{fila_sel['Cuota Pura']}*)

*Detalle de Inversión Inicial:*
* *Suscripción:* {fila_sel['Suscripción']}
* *Cuota Nº 1:* {fila_sel['Cuota 1']}

-----------------------------------------------------------
🔥 *BENEFICIO EXCLUSIVO:* Abonando solo *$400.000, ya cubrís el **INGRESO COMPLETO de Cuota 1 y Suscripción*.
💰 *AHORRO DIRECTO HOY*
-----------------------------------------------------------
Si queda alguna duda a disposición. Para avanzar mándame foto de DNI y reservamos el cupo."""

st.text_area("Copiá este texto:", mensaje_wa, height=300)

if st.button("📋 Copiar para WhatsApp"):
    st.success(f"¡Mensaje de {modelo_sel} listo para pegar!")

