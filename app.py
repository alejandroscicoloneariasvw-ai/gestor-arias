import streamlit as st
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Arias Hnos. | Gestión de Ventas Pro", layout="wide")

# --- ESTILOS UNIFICADOS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Segoe+UI:ital,wght@0,400;0,700;1,300&display=swap');
    html, body, [class*="css"], .stTextArea textarea, .stNumberInput input, .stTextInput input {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
        font-size: 15px !important;
    }
    .firma-scicolone {
        font-family: 'Segoe UI', sans-serif; font-style: italic; font-weight: 300; font-size: 14px;
        color: #6c757d; margin-top: -15px; margin-bottom: 20px; letter-spacing: 0.5px;
    }
    .caja-previa {
        font-family: 'Segoe UI', sans-serif; font-size: 15px; line-height: 1.6; color: #1a1a1b;
        background-color: #ffffff; padding: 25px; border-radius: 12px; border: 1px solid #e0e0e0;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# --- MEMORIA DE SESIÓN ---
if 'lista_precios' not in st.session_state:
    st.session_state.lista_precios = []
if 'fecha_vigencia' not in st.session_state:
    st.session_state.fecha_vigencia = datetime.now().strftime("%d/%m/%Y")

if 'texto_cierre' not in st.session_state:
    st.session_state.texto_cierre = (
        "💳 *DATO CLAVE:* Podés abonar el beneficio con *Tarjeta de Crédito* para patear el pago 30 días. "
        "Además, la Cuota Nº 2 recién te llegará a los *60 días*. ¡Tenés un mes de gracia para acomodar tus gastos! 🚀\\n\\n"
        "✨ *EL CAMBIO QUE MERECÉS:* Más allá del ahorro, imaginate lo que va a ser llegar a casa y ver la cara de orgullo "
        "de tu familia al ver el vehículo nuevo. Hoy estamos a un solo paso. 🥂\\n\\n"
        "⚠️ *IMPORTANTE:* Al momento de enviarte esto, solo me quedan *2 cupos disponibles* con estas condiciones de "
        "abonar un monto menor en la Cuota 1 y Suscripción (Ver Beneficio Exclusivo arriba). 💼✅\\n\\n"
        "🎁 Para asegurar la bonificación del *PRIMER SERVICIO DE MANTENIMIENTO* y el *POLARIZADO DE REGALO*, enviame ahora la foto de tu "
        "**DNI (frente y dorso)**. Yo reservo el cupo mientras terminás de decidirlo, así no perdés el beneficio por falta de stock "
        "y coordinamos el pago del Beneficio Exclusivo. ¡¡¡Arrancá tu nuevo auto y poné primera!!! 🚙🏁🏆✅ ¿Te parece bien? 📝📲"
    )

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("📥 Gestión de Datos")
    modo = st.radio("Acción:", ["Usar datos guardados", "Cargar planilla nueva"], horizontal=True) if st.session_state.lista_precios else "Cargar planilla nueva"

    if modo == "Cargar planilla nueva":
        arc = st.file_uploader("Subir planilla .txt", type=['txt'])
        if arc:
            cont = arc.getvalue().decode("utf-8", errors="ignore")
            lineas = cont.split("\\n")
            temp = []
            for l in lineas:
                if "/" in l and len(l.strip()) <= 10: 
                    st.session_state.fecha_vigencia = l.strip()
                    continue
                p = l.split(",")
                if len(p) >= 8:
                    try:
                        m_f = p[0].strip().upper()
                        adj_ini = "8, 12 y 24" if any(x in m_f for x in ["TERA", "NIVUS", "T-CROSS"]) else ""
                        temp.append({
                            "Modelo": m_f, "VM": int(float(p[1])), "Susc": int(float(p[2])), 
                            "C1": int(float(p[3])), "Adh": int(float(p[4])), "C2_13": int(float(p[5])), 
                            "CFin": int(float(p[6])), "CPura": int(float(p[7])), "Adj_Pactada
