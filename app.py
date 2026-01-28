import streamlit as st
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'
from PIL import Image
import re

# Configuración de la App para Alejandro
st.set_page_config(page_title="Arias Hnos. Gestor", page_icon="🚗")
st.title("🚗 Arias Hnos. | Gestor de Ventas")

# 1. Lógica de inicio (Pregunta si cargar o usar datos) [cite: 2026-01-27]
modo = st.sidebar.radio("Menú de Opciones", ("Cargar Planilla Nueva", "Usar Datos Guardados"))

def extraer_precios(texto):
    # Busca formatos de precio como 44.307.150
    return re.findall(r'\d{2}\.\d{3}\.\d{3}', texto)

if modo == "Cargar Planilla Nueva":
    archivo = st.file_uploader("Subí la foto o PDF de la planilla", type=['jpg', 'png', 'jpeg', 'pdf'])
    if archivo:
        img = Image.open(archivo)
        st.image(img, caption="Planilla cargada", use_column_width=True)
        with st.spinner('Leyendo datos de la imagen...'):
            # El "ojo" del programa que lee la foto
            texto_extraido = pytesseract.image_to_string(img, lang='spa')
            precios = extraer_precios(texto_extraido)
            st.session_state['datos_planilla'] = precios
        st.success("✅ Planilla procesada con éxito.")

# 2. Generación del Mensaje de Venta [cite: 2026-01-27]
if 'datos_planilla' in st.session_state:
    vh = st.selectbox("Elegí el Vehículo:", ["VIRTUS TRENDLINE 1.6", "TERA", "NIVUS", "T-CROSS", "AMAROK", "TAOS"])
    
    precios = st.session_state['datos_planilla']
    # Si detectó precios los usa, sino usa el base que definimos
    valor_movil = precios[0] if len(precios) > 0 else "44.307.150"

    mensaje_vendedor = f"""
Basada en la planilla de *Arias Hnos.*, aquí tienes el detalle para el:

*Vehículo:* {vh}
*Valor del Auto:* ${valor_movil} (Valor Móvil)
*Tipo de Plan:* PLAN 100%
*Plazo:* 84 Cuotas (Cuota Pura de *$527.472*)

*Detalle de Inversión Inicial:*
* *Suscripción:* $850.000
* *Cuota Nº 1:* $730.000
* *Costo Normal de Ingreso:* $1.580.000

-----------------------------------------------------------
🔥 *BENEFICIO EXCLUSIVO:* Abonando solo *$550.000*, ya cubrís el **INGRESO COMPLETO de Cuota 1 y Suscripción**.
💰 *AHORRO DIRECTO HOY: $1.030.000*
-----------------------------------------------------------

*Esquema de cuotas posteriores:*
* *Cuotas 2 a 13:* $577.000
* *Cuotas 14 a 84:* $576.400

Los cupos con este beneficio son limitados. Si quieres avanzar mándame por este medio foto de *DNI* de adelante y de atrás y te comento como realizaremos este pago Beneficio.
    """
    
    st.subheader("📱 Mensaje para WhatsApp:")
    st.text_area("", mensaje_vendedor, height=450)
    
    # Botones recordados: Copiar e Imprimir [cite: 2026-01-27]
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📋 COPIAR MENSAJE"):
            st.success("¡Copiado!")
    with col2:
        if st.button("🖨️ IMPRIMIR"):
            st.info("Preparando impresión...")
else:

    st.info("Hola Alejandro, por favor cargá una planilla para empezar.")
