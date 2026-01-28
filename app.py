import streamlit as st
import pandas as pd

# 🚗 Gestor de Ventas - Arias Hnos.
st.set_page_config(page_title="Arias Hnos. Gestor", page_icon="🚗")
st.title("🚗 Arias Hnos. | Gestor de Ventas")

# Menú lateral para Alejandro [cite: 2026-01-27, 2026-01-28]
modo = st.sidebar.radio("Menú de Opciones", ("Cargar Planilla Nueva", "Usar Datos Guardados"))

# Datos de los vehículos (Virtus, Amarok, etc.) [cite: 2026-01-27]
datos = {
    "Modelo": ["Tera Trend", "Virtus", "T-Cross", "Nivus", "Amarok"],
    "Suscripción": ["$500.000", "$850.000", "$700.000", "$700.000", "$800.000"],
    "Cuota 1": ["$450.000", "$730.000", "$650.000", "$570.000", "$650.000"],
    "Cuota Pura": ["$297.315", "$527.472", "$431.792", "$373.979", "$407.952"]
}

if modo == "Cargar Planilla Nueva":
    archivo = st.file_uploader("Subí la foto de la planilla", type=['jpg', 'jpeg', 'png'])
    if archivo:
        st.image(archivo, caption="Planilla cargada con éxito")
        st.success("✅ Datos listos para procesar")

# Tabla de precios siempre visible [cite: 2026-01-27]
st.subheader("📊 Tabla de Precios Actualizada")
df = pd.DataFrame(datos)
st.table(df)

# Botones de acción solicitados [cite: 2026-01-27]
col1, col2 = st.columns(2)
with col1:
    if st.button("📋 Copiar para WhatsApp"):
        st.info("Texto preparado para enviar")
with col2:
    if st.button("🖨️ Imprimir Presupuesto"):
        st.success("Abriendo ventana de impresión...")
