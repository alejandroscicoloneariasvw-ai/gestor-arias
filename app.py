import streamlit as st

st.set_page_config(page_title="Arias Hnos. | Gestión Pro", layout="wide")

if 'datos' not in st.session_state:
    st.session_state.datos = []

with st.sidebar:
    st.header("📥 Cargar Datos")
    archivo = st.file_uploader("Subí tu planilla .txt", type=['txt'])
    if archivo:
        lineas = archivo.getvalue().decode("utf-8", errors="ignore").split("\n")
        temp = []
        for l in lineas:
            # Esta línea hace que lea el archivo aunque tenga espacios o comas
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

st.title("🚗 Arias Hnos. | Gestión de Ventas")

if st.session_state.datos:
    modelo = st.selectbox("🎯 Elegí el modelo:", [d['Mod'] for d in st.session_state.datos])
    d = next(i for i in st.session_state.datos if i['Mod'] == modelo)
    f = lambda x: f"{x:,}".replace(",", ".")

    tipo = "100%" if "VIRTUS" in d['Mod'] else ("60/40" if "AMAROK" in d['Mod'] else "70/30")
    porc = "40%" if "AMAROK" in d['Mod'] else "30%"
    
    encabezado = f"**Financiá el {tipo} de tu unidad en cuotas y adjudicalo con el {porc} de su valor.**"
    if "100%" in tipo: encabezado = "**Financiá el 100% de tu unidad en cuotas sin necesidad de integración mínima.**"

    txt = (f"Presupuesto Arias Hnos. (Vigencia Marzo 2026)\n\n"
           f"{encabezado}\n\n"
           f"🚘 **Vehículo: {d['Mod']}**\n"
           f"**Valor del Auto: ${f(d['VM'])}**\n\n"
           f"**Inversión Inicial:**\n"
           f"* Suscripción: ${f(d['Susc'])}\n"
           f"* Cuota 1: ${f(d['C1'])}\n\n"
           f"🔥 **BENEFICIO:** Abonando solo **${f(d['Adh'])}** cubrís el ingreso completo.\n\n"
           f"**Cuotas:**\n"
           f"* Cuotas 2-13: ${f(d['C2_13'])}\n"
           f"* Cuotas 14-84: ${f(d['CFin'])}\n"
           f"* Alícuota ({porc}): **Hoy ${f(int(d['VM']*0.4 if "40" in porc else d['VM']*0.3))}**\n\n"
           f"¿Cierro la reserva ahora con tu DNI?")

    st.text_area("📋 Copiá para WhatsApp:", txt, height=350)
else:
    st.info("👋 El sistema está listo. Por favor, subí la planilla en el menú de la izquierda.")
