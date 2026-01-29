import streamlit as st
import pandas as pd
import easyocr
import numpy as np
from PIL import Image
import re

st.set_page_config(page_title="Gestor Arias Hnos.", layout="wide")

# --- FUNCIONES DE LIMPIEZA ---
def limpiar_monto_estricto(texto):
    num = re.sub(r'[^0-9]', '', texto)
    if not num: return None
    valor = int(num)
    # Filtro inteligente: Una cuota/suscripción no vale 20 millones ni 1000 pesos [cite: 2026-01-27]
    if 50000 < valor < 3000000:
        return f"${valor:,}".replace(",", ".")
    # Caso especial: si el OCR leyó un 5 u 8 extra al principio [cite: 2026-01-27]
    if valor > 3000000 and num.startswith(('5', '8', '3')):
        nuevo_valor = int(num[1:])
        if 50000 < nuevo_valor < 3000000:
            return f"${nuevo_valor:,}".replace(",", ".")
    return None

# --- INICIO DEL PROGRAMA --- [cite: 2026-01-27]
st.title("🚗 Sistema Gestor Arias Hnos.")

opcion = st.radio("¿Qué desea hacer?", ["Usar datos guardados", "Cargar una planilla nueva"])

if opcion == "Cargar una planilla nueva":
    archivo = st.file_uploader("Subí la foto o PDF de la planilla", type=['jpg', 'png', 'jpeg'])
    if archivo:
        with st.spinner('🤖 Procesando nueva planilla...'):
            reader = easyocr.Reader(['es'])
            img = Image.open(archivo)
            res = reader.readtext(np.array(img), detail=0)
            
            modelos = ["TERA", "VIRTUS", "T-CROSS", "NIVUS", "AMAROK", "TAOS"]
            datos = {m: {"Susc": "$0", "C1": "$0"} for m in modelos}
            
            mod_actual = None
            for i, texto in enumerate(res):
                t_up = texto.upper()
                for mod in modelos:
                    if mod in t_up: mod_actual = mod
                
                if mod_actual:
                    # Buscamos Suscripción: el precio suele ser el primer número después [cite: 2026-01-27]
                    if "SUSC" in t_up:
                        for k in range(1, 4):
                            if i+k < len(res):
                                p = limpiar_monto_estricto(res[i+k])
                                if p: 
                                    datos[mod_actual]["Susc"] = p
                                    break
                    # Buscamos Cuota 1: ídem anterior [cite: 2026-01-28]
                    if "CUOTA N" in t_up and "1" in t_up:
                        for k in range(1, 4):
                            if i+k < len(res):
                                p = limpiar_monto_estricto(res[i+k])
                                if p:
                                    datos[mod_actual]["C1"] = p
                                    break
            
            # Guardamos en la "memoria" del programa [cite: 2026-01-27]
            st.session_state.ultimos_datos = datos
            st.success("✅ Planilla cargada y guardada.")

# --- MOSTRAR RESULTADOS ---
if 'ultimos_datos' in st.session_state:
    datos_mostrar = st.session_state.ultimos_datos
    df = pd.DataFrame([
        {"Modelo": m, "Suscripción": datos_mostrar[m]["Susc"], "Cuota 1": datos_mostrar[m]["C1"]}
        for m in datos_mostrar
    ])
    
    st.subheader("📊 Planilla en Memoria")
    st.table(df)

    # --- SECCIÓN WHATSAPP --- [cite: 2026-01-27, 2026-01-28]
    st.divider()
    sel = st.selectbox("Seleccioná un modelo para el mensaje:", list(datos_mostrar.keys()))
    
    txt_ws = f"*Arias Hnos. | Precios Actualizados*\n\n*Modelo:* {sel}\n✅ *Suscripción:* {datos_mostrar[sel]['Susc']}\n✅ *Cuota 1:* {datos_mostrar[sel]['C1']}"
    
    st.text_area("Mensaje listo para copiar:", txt_ws)
    if st.button("📋 Copiar Mensaje"):
        st.write("Copiá el texto de arriba manualmente (Seleccionar + Ctrl+C)")
    
    link = f"https://wa.me/?text={txt_ws.replace(' ', '%20').replace('\n', '%0A')}"
    st.markdown(f"[📲 Enviar directo a WhatsApp]({link})")
else:
    if opcion == "Usar datos guardados":
        st.info("No hay datos previos. Por favor, cargá una planilla nueva primero.")

if st.sidebar.button("🗑️ Borrar Memoria"):
    if 'ultimos_datos' in st.session_state:
        del st.session_state.ultimos_datos
    st.rerun()
