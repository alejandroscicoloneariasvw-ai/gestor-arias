import streamlit as st
import pandas as pd
import easyocr
import numpy as np
from PIL import Image
import re

st.set_page_config(page_title="Arias Hnos. | Lector Pro", layout="wide")
st.title("🚗 Arias Hnos. | Sistema de Precios")

# Cargamos el lector una sola vez para que sea rápido
@st.cache_resource
def get_reader():
    return easyocr.Reader(['es'])

reader = get_reader()

def limpiar_precio_real(texto):
    num = re.sub(r'[^0-9]', '', texto)
    # Si el número es muy corto, no es un precio (ej: "84" meses) [cite: 2026-01-27]
    if len(num) < 5: return None
    # Quitamos el 5, 8 o 3 inicial que suele ser error del signo $ [cite: 2026-01-27]
    if len(num) >= 7 and num.startswith(('5', '8', '3')):
        num = num[1:]
    
    # Formateamos con puntos para que se lea bien
    return f"${int(num):,}".replace(",", ".")

# --- LA CLAVE: El uploader no guarda estados viejos ---
archivo = st.file_uploader("Subí la planilla", type=['jpg', 'jpeg', 'png'])

if archivo:
    # Mostramos la imagen actual
    st.image(archivo, width=350, caption="Procesando esta imagen ahora...")
    
    with st.spinner('🤖 Leyendo datos frescos...'):
        # 1. Forzamos la lectura limpia
        img = Image.open(archivo)
        res = reader.readtext(np.array(img), detail=0)
        
        # 2. Creamos la estructura de datos VACÍA cada vez [cite: 2026-01-27]
        modelos = ["TERA", "VIRTUS", "T-CROSS", "NIVUS", "AMAROK", "TAOS"]
        datos_foto = {m: {"Susc": "$0", "C1": "$0"} for m in modelos}
        
        if res:
            modelo_actual = None
            for i, texto in enumerate(res):
                t_up = texto.upper()
                
                # Identificamos el auto
                for mod in modelos:
                    if mod in t_up:
                        modelo_actual = mod
                
                if modelo_actual:
                    # Buscamos Suscripción
                    if any(x in t_up for x in ["SUSC", "SCRIP", "SU5C"]):
                        for k in range(1, 4): # Buscamos en los 3 renglones siguientes
                            if i+k < len(res):
                                p = limpiar_precio_real(res[i+k])
                                if p: 
                                    datos_actual = p
                                    datos_foto[modelo_actual]["Susc"] = p
                                    break
                    
                    # Buscamos Cuota 1
                    if any(x in t_up for x in ["CUOTA N", "CUOTAN", "CU0TA"]):
                        for k in range(1, 4):
                            if i+k < len(res):
                                p = limpiar_precio_real(res[i+k])
                                if p:
                                    datos_foto[modelo_actual]["C1"] = p
                                    break

            # 3. Mostramos la tabla RECIÉN CREADA [cite: 2026-01-28]
            df_final = pd.DataFrame([
                {"Modelo": m, "Suscripción": datos_foto[m]["Susc"], "Cuota 1": datos_foto[m]["C1"]}
                for m in modelos
            ])
            
            st.subheader("📊 Precios de la planilla cargada:")
            st.table(df_final)
            st.success("✅ ¡Actualizado correctamente!")
        else:
            st.warning("No se detectó texto. Intentá de nuevo.")

# Botón de reset total por si el servidor se tilda
if st.sidebar.button("♻️ Reiniciar Sistema"):
    st.cache_resource.clear()
    st.rerun()
