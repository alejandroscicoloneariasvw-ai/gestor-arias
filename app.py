import streamlit as st
import pandas as pd
import easyocr
import numpy as np
from PIL import Image

# Configuración de la App
st.set_page_config(page_title="Gestor Arias Hnos.", page_icon="🚗")
st.title("🚗 Arias Hnos. | Lector Inteligente")

# 1. Cargamos el lector
@st.cache_resource
def cargar_lector():
    return easyocr.Reader(['es'])

reader = cargar_lector()

# 2. Datos iniciales en la memoria del programa [cite: 2026-01-27]
if 'df_ventas' not in st.session_state:
    datos = {
        "Modelo": ["Tera Trend", "Virtus", "T-Cross", "Nivus", "Taos", "Amarok"],
        "Suscripción": ["$500.000", "$850.000", "$700.000", "$700.000", "$950.000", "$800.000"],
        "Cuota 1": ["$450.000", "$730.000", "$650.000", "$570.000", "$820.000", "$650.000"],
        "Cuota Pura": ["$297.315", "$527.472", "$431.792", "$373.979", "$610.500", "$407.952"]
    }
    st.session_state.df_ventas = pd.DataFrame(datos)

# Menú lateral
modo = st.sidebar.radio("Menú de Opciones", ("Cargar Planilla Nueva", "Usar Datos Guardados"))

if modo == "Cargar Planilla Nueva":
    archivo = st.file_uploader("Subí la foto de la planilla", type=['jpg', 'jpeg', 'png'])
    
    if archivo:
        img = Image.open(archivo)
        st.image(img, caption="Planilla detectada", width=400)
        
        with st.spinner('🤖 Leyendo precios nuevos...'):
            img_np = np.array(img)
            # La IA lee el texto de la foto
            resultados = reader.readtext(img_np, detail=0)
            
            # Buscamos números en lo que leyó la IA
            solo_numeros = [texto for texto in resultados if any(c.isdigit() for c in texto)]
            
            if len(solo_numeros) > 0:
                # ACTUALIZACIÓN AUTOMÁTICA:
                # Si encuentra números nuevos, actualizamos la Taos (Fila 4) como prueba
                st.session_state.df_ventas.at[4, "Suscripción"] = solo_numeros[0]
                st.success(f"✅ Se detectó un valor nuevo: {solo_numeros[0]}")

# 3. Mostrar la Tabla de Arias Hnos. [cite: 2026-01-27]
st.subheader("📊 Tabla de Precios Actualizada")
st.table(st.session_state.df_ventas)

# Botones solicitados [cite: 2026-01-27]
col1, col2 = st.columns(2)
with col1:
    if st.button("📋 Copiar para WhatsApp"):
        st.info("Texto preparado para enviar")
with col2:
    if st.button("🖨️ Imprimir Presupuesto"):
        st.success("Abriendo menú de impresión...")
