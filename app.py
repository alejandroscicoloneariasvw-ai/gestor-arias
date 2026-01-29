import streamlit as st
import pandas as pd
import easyocr
import numpy as np
from PIL import Image
import re

st.set_page_config(page_title="Arias Hnos. | Gestión de Datos", layout="wide")
st.title("🚗 Arias Hnos. | Sistema de Precios Profesional")

@st.cache_resource
def get_reader():
    return easyocr.Reader(['es'])

reader = get_reader()

def limpiar_precio(texto):
    num = re.sub(r'[^0-9]', '', texto)
    if not num or len(num) < 5 or len(num) > 7: return None
    if len(num) == 7 and num.startswith(('5', '8', '3')): num = num[1:]
    return int(num)

# --- MENÚ DE NAVEGACIÓN ---
menu = st.sidebar.radio("Seleccioná Tarea:", ["1. Procesar Planilla Nueva", "2. Trabajar con Datos Guardados"])

# --- VARIABLES DE SESIÓN ---
if 'datos_mes' not in st.session_state:
    st.session_state.datos_mes = None

# --- OPCIÓN 1: EXTRACCIÓN Y GENERACIÓN DE ARCHIVO ---
if menu == "1. Procesar Planilla Nueva":
    st.header("📸 Extractor de Imagen a Texto")
    archivo_img = st.file_uploader("Subí la planilla (Amarilla o Roja)", type=['jpg', 'jpeg', 'png'])
    
    if archivo_img:
        with st.spinner('🤖 Extrayendo datos...'):
            img = Image.open(archivo_img)
            res = reader.readtext(np.array(img), detail=0)
            
            modelos = ["TERA", "VIRTUS", "T-CROSS", "NIVUS", "AMAROK", "TAOS"]
            lineas_txt = []
            
            for i, texto in enumerate(res):
                t_up = texto.upper()
                for m in modelos:
                    if m in t_up:
                        encontrados = []
                        for j in range(1, 20):
                            if i + j < len(res):
                                p = limpiar_precio(res[i+j])
                                if p and p not in encontrados: encontrados.append(p)
                                if len(encontrados) == 4: break
                        
                        if len(encontrados) == 4:
                            linea = f"{m},{encontrados[0]},{encontrados[1]},{encontrados[2]},{encontrados[3]}"
                            lineas_txt.append(linea)

            contenido_txt = "\n".join(lineas_txt)
            
            st.warning("⚠️ Revisá que los números coincidan con la foto. Podés editarlos acá abajo directamente.")
            editado = st.text_area("Formato: MODELO,Suscripción,Cuota1,Cuota2-13,Cuota14-84", contenido_txt, height=200)
            
            st.download_button(
                label="💾 DESCARGAR ARCHIVO TXT (Maestro del Mes)",
                data=editado,
                file_name="precios_autos.txt",
                mime="text/plain"
            )

# --- OPCIÓN 2: CARGAR EL TXT Y USAR EL PROGRAMA ---
elif menu == "2. Trabajar con Datos Guardados":
    st.header("📂 Panel de Ventas")
    archivo_txt = st.file_uploader("Subí tu archivo de precios (.txt)", type=['txt'])
    
    if archivo_txt:
        stringio = archivo_txt.getvalue().decode("utf-8")
        filas = [f for f in stringio.split("\n") if f.strip()]
        
        datos_para_tabla = {}
        for f in filas:
            p = f.split(",")
            if len(p) == 5:
                datos_para_tabla[p[0]] = {
                    "Susc": f"${int(p[1]):,}".replace(",", "."),
                    "C1": f"${int(p[2]):,}".replace(",", "."),
                    "C2_13": f"${int(p[3]):,}".replace(",", "."),
                    "C14_84": f"${int(p[4]):,}".replace(",", ".")
                }
        
        # Mostrar Tabla
        df_list = [{"Modelo": k, "Suscripción": v["Susc"], "Cuota 1": v["C1"], "C 2-13": v["C2_13"], "C 14-84": v["C14_84"]} for k, v in datos_para_tabla.items()]
        st.table(pd.DataFrame(df_list))
        
        st.divider()
        
        # WhatsApp
        sel = st.selectbox("Elegí el auto para enviar presupuesto:", list(datos_para_tabla.keys()))
        d = datos_para_tabla[sel]
        msj = (f"*Arias Hnos.*\n*Auto:* {sel}\n"
               f"✅ *Suscripción:* {d['Susc']}\n"
               f"✅ *Cuota 1:* {d['C1']}\n"
               f"✅ *Cuotas 2 a 13:* {d['C2_13']}\n"
               f"✅ *Cuotas 14 a 84:* {d['C14_84']}")
        
        st.text_area("Mensaje listo para copiar:", msj, height=150)
        st.markdown(f"[📲 Enviar por WhatsApp](https://wa.me/?text={msj.replace(' ', '%20').replace('\n', '%0A')})")
