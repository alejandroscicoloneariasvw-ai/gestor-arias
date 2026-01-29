import streamlit as st
import pandas as pd
import easyocr
import numpy as np
from PIL import Image
import re

st.set_page_config(page_title="Gestor Arias Hnos.", page_icon="🚗")
st.title("🚗 Arias Hnos. | Lector de Planillas")

# 1. Cargamos el motor de lectura (solo una vez)
@st.cache_resource
def get_reader():
    return easyocr.Reader(['es'])

reader = get_reader()

def limpiar_monto(texto):
    num = re.sub(r'[^0-9.]', '', texto)
    if len(num) >= 7 and num.startswith(('5', '8', '3')):
        num = num[1:]
    return f"${num}" if num else "$0"

# --- INTERFAZ ---
# Usamos un 'key' dinámico basado en el archivo para forzar el reinicio [cite: 2026-01-27]
archivo = st.file_uploader("Subí la planilla de Arias Hnos.", type=['jpg', 'jpeg', 'png'])

if archivo:
    st.image(archivo, width=300, caption="Planilla actual")
    
    with st.spinner('🤖 Analizando nueva planilla...'):
        # Convertimos imagen y leemos
        img_pil = Image.open(archivo)
        res = reader.readtext(np.array(img_pil), detail=0)
        
        if res:
            st.write(f"✅ Se detectaron {len(res)} líneas de texto.")
            
            # Preparamos la estructura de datos limpia [cite: 2026-01-28]
            modelos = ["TERA", "VIRTUS", "T-CROSS", "NIVUS", "AMAROK", "TAOS"]
            tabla_datos = []
            
            for mod in modelos:
                susc = "$0"
                c1 = "$0"
                
                # Buscamos el modelo en la lectura
                for i, linea in enumerate(res):
                    if mod in linea.upper():
                        # Una vez encontrado el auto, buscamos sus datos abajo [cite: 2026-01-27]
                        for j in range(i+1, min(i+20, len(res))):
                            # Buscamos Suscripción (más flexible con el texto)
                            if "SUSCR" in res[j].upper() and j+1 < len(res):
                                susc = limpiar_monto(res[j+1])
                            # Buscamos Cuota 1
                            if "CUOTA NO" in res[j].upper() and j+1 < len(res):
                                if "." in res[j+1] and len(res[j+1]) > 4:
                                    c1 = limpiar_monto(res[j+1])
                                    break # Salimos del bucle de este auto
                
                tabla_datos.append({"Modelo": mod, "Suscripción": susc, "Cuota 1": c1})

            # Creamos el DataFrame y lo mostramos
            df_final = pd.DataFrame(tabla_datos)
            st.subheader("📊 Tabla Actualizada")
            st.table(df_final)
            
        else:
            st.error("❌ El lector no pudo extraer texto de esta imagen. Probá con una foto más clara.")

# Botón para limpiar memoria si se traba
if st.sidebar.button("♻️ Reiniciar Todo"):
    st.cache_resource.clear()
    st.rerun()
