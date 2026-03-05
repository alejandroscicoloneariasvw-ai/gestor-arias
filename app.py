import streamlit as st

st.set_page_config(page_title="Arias Hnos. | Gestión de Ventas Pro", layout="wide")

# Estilo para el "By Alejandro"
st.markdown("""
    <style>
    .footer { position: fixed; bottom: 10px; right: 10px; font-size: 12px; color: gray; }
    </style>
    <div class="footer">By Alejandro Scicolone</div>
    """, unsafe_allow_html=True)

if 'datos' not in st.session_state:
    st.session_state.datos = []

with st.sidebar:
    st.header("📥 Cargar Datos")
    archivo = st.file_uploader("Subir planilla .txt", type=['txt'])
    
    if archivo:
        lineas = archivo.getvalue().decode("utf-8", errors="ignore").split("\n")
        temp = []
        for l in lineas:
            p = l.replace("\t", ",").replace("  ", ",").split(",")
            p = [x.strip() for x in p if x.strip()]
            if len(p) >= 8:
                try:
                    temp.append({
                        "Mod": p[0].upper(), "VM": int(float(p[1])), "Susc": int(float(p[2])),
                        "C1": int(float(p[3])), "Adh": int(float(p[4])), "C2_13": int(float(p[5])),
                        "CFin": int(float(p[6])), "CPura": int(float(p[7]))
                    })
                except: continue
        st.session_state.datos = temp
    
    st.write("---")
    st.subheader("🛠️ Modificaciones")
    st.write("- Agregado de negritas persuasivas")
    st.write("- Beneficio de Cuota 1 y Adhesión")
    st.write("- Cierre con pedido de DNI")
    st.write("- Texto de Alícuota con 'Hoy'")

st.title("🚗 Arias Hnos. | Gestión de Ventas")

if st.session_state.datos:
    modelo = st.selectbox("🎯 Seleccioná el modelo para el presupuesto:", [d['Mod'] for d in st.session_state.datos])
    d = next(i for i in st.session_state.datos if i['Mod'] == modelo)
    f = lambda x: f"{x:,}".replace(",", ".")

    # Lógica de porcentaje y tipo
    tipo = "100%" if "VIRTUS" in d['Mod'] else ("60/40" if "AMAROK" in d['Mod'] else "70/30")
    porc = "40%" if "AMAROK" in d['Mod'] else "30%"
    alic_valor = int(d['VM'] * 0.4 if "40" in porc else d['VM'] * 0.3)
    
    # Encabezado con negritas
    encabezado = f"**Financiá el {tipo} de tu unidad en cuotas y adjudicalo con el {porc} de su valor.**"
    if "100%" in tipo: encabezado = "**Financiá el 100% de tu unidad en cuotas sin necesidad de integración mínima.**"

    # TEXTO PARA WHATSAPP
    txt = (f"🏛️ *Presupuesto Arias Hnos.* (Vigencia Marzo 2026)\n\n"
           f"{encabezado}\n\n"
           f"🚘 **Vehículo: {d['Mod']}**\n"
           f"💰 **Valor de Lista: ${f(d['VM'])}**\n\n"
           f"⭐ **INVERSIÓN INICIAL:**\n"
           f"* Suscripción: ${f(d['Susc'])}\n"
           f"* Cuota 1: ${f(d['C1'])}\n\n"
           f"🔥 **BENEFICIO EXCLUSIVO:** Abonando solo **${f(d['Adh'])}** cubrís el ingreso completo a la unidad.\n\n"
           f"📈 **ESQUEMA DE CUOTAS:**\n"
           f"* Cuotas 2 a 13: ${f(d['C2_13'])}\n"
           f"* Cuotas 14 a 84: ${f(d['CFin'])}\n"
           f"* Alícuota Extraordinaria ({porc}): **Hoy ${f(alic_valor)}**\n\n"
           f"✅ *Valor de cuota pura para licitar: ${f(d['CPura'])}*\n\n"
           f"¿Cierro la reserva ahora con tu DNI para congelar estos valores?\n\n"
           f"Atentamente,\n"
           f"👤 **Alejandro Scicolone**\n"
           f"📍 Arias Hnos. Volkswagen")

    st.text_area("📋 Copiá para WhatsApp:", txt, height=450)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Nueva Carga"):
            st.session_state.datos = []
            st.rerun()
else:
    st.info("👋 El sistema está listo. Por favor, cargá la planilla desde el menú de la izquierda para empezar.")
