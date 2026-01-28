import streamlit as st
import pandas as pd
import easyocr
import numpy as np
from PIL import Image
import re

st.set_page_config(page_title="Gestor Arias Hnos.", page_icon="🚗")
st.title("🚗 Arias Hnos. | Lector Inteligente")

@st.cache_resource
def cargar_lector():
    return easyocr.Reader(['es'])

reader = cargar_lector()

if 'df_ventas' not in st.session_state:
    datos = {
        "Modelo": ["Tera Trend", "Virtus", "T-Cross", "Nivus", "Taos", "Amarok"],
        "Suscripción": ["$500.000", "$850.000", "$700.000", "$700.000", "$950.000", "$800.000"],
        "Cuota 1": ["$450.000", "$730.000", "$650.000", "$570.000", "$820.000", "$650.000"],
        "Cuota Pura": ["$297.315", "$527.472", "$431.792", "$373.979", "$610.500", "$407.952"]
    }
    st.session_state.df_ventas = pd.DataFrame(datos)

modo = st.sidebar.radio("Menú de Opciones", ("Cargar Planilla Nueva", "Usar Datos Guardados"))

if modo == "Cargar Planilla Nueva":
    archivo = st.file_uploader("Subí la planilla", type=['jpg', 'jpeg', 'png'])
    
    if archivo:
        img = Image.open(archivo)
        st.image(img, caption="Analizando planilla de Arias Hnos...", width=400)
        
        with st.spinner('🤖 Buscando precios...'):
            img_np = np.array(img)
            resultados = reader.readtext(img_np, detail=0)
            
            # 🎯 Lógica mejorada: Buscamos números que tengan puntos (ej: 800.000) 
            # y que NO tengan barras de fecha (/)
            precios_reales = []
            for texto in resultados:
                limpio = texto.replace("$", "").strip()
                if "." in limpio and "/" not in limpio:
                    precios_reales.append(f"${limpio}")

            if len(precios_reales) >= 3:
                # Si es la planilla de la Taos:
                st.session_state.df_ventas.at[4, "Suscripción"] = precios_reales[0]
                st.session_state.df_ventas.at[4, "Cuota 1"] = precios_reales[1]
                st.session_state.df_ventas.at[4, "Cuota Pura"] = precios_reales[2]
                st.success(f"✅ Taos actualizada: Susc. {precios_reales[0]} | Cuota 1 {precios_reales[1]}")

st.subheader("📊 Tabla de Precios Actualizada")
st.table(st.session_state.df_ventas)

col1, col2 = st.columns(2)
with col1:
    st.button("📋 Copiar para WhatsApp")
with col2:
    st.button("🖨️ Imprimir Presupuesto")
