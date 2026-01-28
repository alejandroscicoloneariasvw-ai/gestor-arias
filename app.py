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
        st.image(img, caption="Analizando planilla...", width=400)
        
        with st.spinner('🤖 Extrayendo precios reales...'):
            img_np = np.array(img)
            resultados = reader.readtext(img_np, detail=0)
            
            # 🎯 FILTRO DE SEGURIDAD: Solo números con puntos y sin letras
            precios_detectados = []
            for t in resultados:
                # Quitamos el signo $ y espacios
                limpio = t.replace("$", "").replace(" ", "").strip()
                # Si tiene puntos y al menos un número, y NO tiene letras, es un precio
                if "." in limpio and any(c.isdigit() for c in limpio) and not any(c.isalpha() for c in limpio):
                    precios_detectados.append(f"${limpio}")

            if len(precios_detectados) >= 3:
                # Actualizamos la Taos con los primeros 3 precios limpios encontrados en la foto
                st.session_state.df_ventas.at[4, "Suscripción"] = precios_detectados[0]
                st.session_state.df_ventas.at[4, "Cuota 1"] = precios_detectados[1]
                st.session_state.df_ventas.at[4, "Cuota Pura"] = precios_detectados[2]
                st.success(f"✅ Precios de Taos actualizados: {precios_detectados[0]}, {precios_detectados[1]}, {precios_detectados[2]}")
            else:
                st.warning("⚠️ No pude distinguir los precios claramente. Intentá con una foto más de cerca.")

st.subheader("📊 Tabla de Precios Actualizada")
st.table(st.session_state.df_ventas)

col1, col2 = st.columns(2)
with col1:
    st.button("📋 Copiar para WhatsApp")
with col2:
    st.button("🖨️ Imprimir Presupuesto")
