import streamlit as st
import pandas as pd
import easyocr
import numpy as np
from PIL import Image
import re

st.set_page_config(page_title="Gestor Arias Hnos.", layout="wide")
st.title("🚗 Sistema Gestor Arias Hnos.")

# 1. Cargador del motor (Lector)
@st.cache_resource
def cargar_lector():
    return easyocr.Reader(['es'])

reader = cargar_lector()

def limpiar_precio(texto):
    # Solo números y puntos
    num = re.sub(r'[^0-9.]', '', texto)
    # Si el OCR leyó un 5, 8 o 3 extra al inicio (error común con el $)
    if len(num) >= 7 and num.startswith(('5', '8', '3')):
        num = num[1:]
    return f"${num}" if num else "$0"

# --- INTERFAZ ---
# Agregamos un botón para limpiar todo manualmente si hace falta
if st.sidebar.button("♻️ Reiniciar para nueva planilla"):
    st.cache_data.clear()
    st.session_state.clear()
    st.rerun()

# El secreto para la 2da carga: un 'key' que cambia [cite: 2026-01-27]
archivo = st.file_uploader("Subí tu planilla (Amarilla o Color)", type=['jpg', 'jpeg', 'png'])

if archivo:
    img = Image.open(archivo)
    st.image(img, width=350, caption="Planilla actual")
    
    with st.spinner('🤖 Leyendo datos...'):
        # Leemos la imagen
        res = reader.readtext(np.array(img), detail=0)
        
        modelos = ["TERA", "VIRTUS", "T-CROSS", "NIVUS", "AMAROK", "TAOS"]
        datos_finales = {m: {"Susc": "$0", "C1": "$0"} for m in modelos}
        
        if res:
            mod_actual = None
            for i, texto in enumerate(res):
                t_up = texto.upper()
                
                # Identificamos el auto
                for mod in modelos:
                    if mod in t_up:
                        mod_actual = mod
                
                if mod_actual:
                    # Lógica original: El precio está JUSTO después de la palabra clave [cite: 2026-01-27]
                    if "SUSCRIP" in t_up and i+1 < len(res):
                        datos_finales[mod_actual]["Susc"] = limpiar_precio(res[i+1])
                    
                    if "CUOTA N" in t_up and i+1 < len(res):
                        # Verificamos que no sea el "84" de los meses
                        posible_precio = res[i+1]
                        if len(re.sub(r'[^0-9]', '', posible_precio)) > 4:
                            datos_finales[mod_actual]["C1"] = limpiar_precio(posible_precio)

            # Mostramos la tabla [cite: 2026-01-28]
            df = pd.DataFrame([
                {"Modelo": m, "Suscripción": datos_finales[m]["Susc"], "Cuota 1": datos_finales[m]["C1"]}
                for m in modelos
            ])
            
            st.subheader("📊 Resultados de la Planilla")
            st.table(df)

            # --- WHATSAPP --- [cite: 2026-01-27]
            st.divider()
            sel = st.selectbox("Seleccioná el modelo para enviar:", modelos)
            msj = f"*Arias Hnos. | Detalle*\n\n*Modelo:* {sel}\n✅ *Suscripción:* {datos_finales[sel]['Susc']}\n✅ *Cuota 1:* {datos_finales[sel]['C1']}"
            
            st.text_area("Mensaje:", msj, height=100)
            st.markdown(f"[📩 Enviar a WhatsApp](https://wa.me/?text={msj.replace(' ', '%20').replace('\n', '%0A')})")

else:
    st.info("Por favor, subí una planilla para comenzar.")
