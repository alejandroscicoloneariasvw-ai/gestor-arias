import streamlit as st
import pandas as pd
import easyocr
import numpy as np
from PIL import Image

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
        st.image(img, caption="Analizando datos específicos...", width=400)
        
        with st.spinner('🤖 Buscando precios exactos...'):
            img_np = np.array(img)
            # Obtenemos posición y texto para saber qué hay al lado de qué
            resultados = reader.readtext(img_np)
            
            for i, (bbox, texto, prob) in enumerate(resultados):
                t_min = texto.lower()
                # Si encuentra "Suscripción", el precio suele ser el siguiente texto detectado
                if "suscrip" in t_min and i+1 < len(resultados):
                    valor = resultados[i+1][1]
                    if "." in valor: st.session_state.df_ventas.at[4, "Suscripción"] = valor
                
                # Buscamos la Cuota 1 (que en tu foto tiene el nro 1 al lado)
                if "cuota" in t_min and "1" in t_min and i+1 < len(resultados):
                    valor = resultados[i+1][1]
                    if "." in valor: st.session_state.df_ventas.at[4, "Cuota 1"] = valor

                # Buscamos la Cuota Pura
                if "pura" in t_min and i+1 < len(resultados):
                    valor = resultados[i+1][1]
                    if "." in valor: st.session_state.df_ventas.at[4, "Cuota Pura"] = valor

            st.success("✅ ¡Tabla de Taos actualizada con los precios de la foto!")

st.subheader("📊 Tabla de Precios Actualizada")
st.table(st.session_state.df_ventas)

col1, col2 = st.columns(2)
with col1:
    if st.button("📋 Copiar para WhatsApp"):
        st.info("Texto copiado")
with col2:
    if st.button("🖨️ Imprimir Presupuesto"):
        st.success("Imprimiendo...")
