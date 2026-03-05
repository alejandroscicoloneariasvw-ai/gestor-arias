import streamlit as st

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Arias Hnos. | Gestión de Ventas Pro", layout="wide")

# --- MEMORIA ---
if 'lista_precios' not in st.session_state: st.session_state.lista_precios = []
if 'fecha_vigencia' not in st.session_state: st.session_state.fecha_vigencia = "04/03/2026"

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("📥 Cargar Datos")
    arc = st.file_uploader("Subir planilla .txt", type=['txt'])
    if arc:
        cont = arc.getvalue().decode("utf-8", errors="ignore")
        lineas = cont.split("\n")
        temp = []
        for l in lineas:
            if "/" in l and len(l.strip()) <= 10: st.session_state.fecha_vigencia = l.strip(); continue
            p = l.split(",")
            if len(p) >= 8:
                try:
                    m_f = p[0].strip().upper()
                    adj_ini = "8, 12 y 24" if any(x in m_f for x in ["TERA", "NIVUS", "T-CROSS"]) else ""
                    temp.append({"Modelo": m_f, "VM": int(float(p[1])), "Susc": int(float(p[2])), "C1": int(float(p[3])), "Adh": int(float(p[4])), "C2_13": int(float(p[5])), "CFin": int(float(p[6])), "CPura": int(float(p[7])), "Adj_Pactada": adj_ini})
                except: continue
        st.session_state.lista_precios = temp
        st.rerun()

# --- CUERPO ---
if st.session_state.lista_precios:
    mod_sel = st.selectbox("🎯 Seleccionar Modelo:", [a['Modelo'] for a in st.session_state.lista_precios])
    d = next(a for a in st.session_state.lista_precios if a['Modelo'] == mod_sel)
    fmt = lambda x: f"{x:,}".replace(",", ".")
    
    # --- LÓGICA DE TEXTO RESALTADO ---
    encabezado_plan = ""
    alicuota_txt = ""
    if "VIRTUS" in d['Modelo']: 
        encabezado_plan = f"**Financiá el 100% de tu unidad en cuotas sin necesidad de integración mínima.**\n\n"
    elif any(x in d['Modelo'] for x in ["AMAROK", "TAOS"]): 
        encabezado_plan = f"**Financiá hasta el 60% de tu unidad en cuotas y adjudicalo con el 40% de su valor.**\n\n"
        alicuota_txt = f"* *Alícuota Extraordinaria (40%):* **Hoy ${fmt(int(d['VM']*0.40))}** (Se abona al adjudicar)\n"
    elif any(x in d['Modelo'] for x in ["TERA", "NIVUS", "T-CROSS"]): 
        encabezado_plan = f"**Financiá hasta el 70% de tu unidad en cuotas y adjudicalo con el 30% de su valor.**\n\n"
        alicuota_txt = f"* *Alícuota Extraordinaria (30%):* **Hoy ${fmt(int(d['VM']*0.30))}** (Se abona al adjudicar)\n"

    msj = (f"Basada en la planilla de *Arias Hnos.* con vigencia al **{st.session_state.fecha_vigencia}**:\n\n"
           f"{encabezado_plan}" # <--- ESTO VA PRIMERO Y EN NEGRITA
           f"🚘 **Vehículo: {d['Modelo']}**\n"
           f"**Valor del Auto: ${fmt(d['VM'])}**\n\n"
           f"**Detalle de Inversión Inicial:**\n"
           f"* Suscripción: ${fmt(d['Susc'])}\n"
           f"* Cuota Nº 1: ${fmt(d['C1'])}\n\n"
           f"-----------------------------------------------------------\n"
           f"🔥 **BENEFICIO EXCLUSIVO:** Abonando solo **${fmt(d['Adh'])}**, ya cubrís el **INGRESO COMPLETO**.\n"
           f"-----------------------------------------------------------\n\n"
           f"**Cuotas posteriores:**\n"
           f"* Cuotas 2 a 13: ${fmt(d['C2_13'])}\n"
           f"* Cuotas 14 a 84: ${fmt(d['CFin'])}\n"
           f"{alicuota_txt}") # <--- ACÁ DICE "HOY"

    st.text_area("Copiá el mensaje desde acá:", msj, height=400)
else:
    st.info("Cargá la planilla para empezar.")
