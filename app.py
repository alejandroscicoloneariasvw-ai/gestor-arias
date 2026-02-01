import streamlit as st
import pandas as pd

# --- TÍTULO DEL PROGRAMA ---
# Usando el formato directo "by Alejandro Scicolone"
st.title("Sistema de Planillas by Alejandro Scicolone")

st.write("---")

# --- LÓGICA DE CARGA (Tu requerimiento específico) ---
opcion = st.radio(
    "¿Qué desea hacer?",
    ("Usar datos guardados", "Cargar una planilla nueva")
)

if opcion == "Cargar una planilla nueva":
    archivo = st.file_uploader("Suba la foto o PDF de la planilla", type=["pdf", "jpg", "png", "jpeg"])
    if archivo:
        st.success("Planilla cargada correctamente.")
else:
    st.info("Utilizando la última planilla cargada.")

st.write("---")

# --- BOTONES DE ACCIÓN ---
col1, col2 = st.columns(2)

with col1:
    if st.button("Copiar"):
        # Lógica para copiar los datos
        st.write("Datos copiados al portapapeles.")

with col2:
    if st.button("Imprimir"):
        # Lógica para imprimir
        st.write("Preparando documento para imprimir...")

# --- ÁREA DE DATOS ---
# Aquí se muestran los datos procesados
st.subheader("Datos de la Planilla")
# (Espacio para la tabla de datos)
