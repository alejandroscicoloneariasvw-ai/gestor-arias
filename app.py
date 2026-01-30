import streamlit as st
import pandas as pd

st.set_page_config(page_title="Arias Hnos. | Gestión de Ventas", layout="wide")

st.title("🚗 Arias Hnos. | Presupuestador")

# Preguntar si quiere cargar nueva planilla o usar la anterior
opcion = st.radio("¿Qué desea hacer?", ["Cargar nueva planilla", "Usar datos guardados"])

if opcion == "Cargar nueva planilla":
    archivo = st.file_input("Suba el archivo TXT de la planilla", type=["txt"])
    if archivo is not None:
        # Aquí procesamos la planilla
        st.success("Planilla cargada con éxito")
else:
    st.info("Utilizando la última planilla cargada.")

# Botones que pediste
col1, col2 = st.columns(2)
with col1:
    if st.button("Copiar Presupuesto"):
        st.write("Copiado al portapapeles (Simulado)")
with col2:
    if st.button("Imprimir"):
        st.write("Enviando a imprimir...")

st.write("---")
st.caption("Desarrollado para Alejandro - Arias Hnos. 2026")
