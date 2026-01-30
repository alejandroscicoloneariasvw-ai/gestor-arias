import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Arias Hnos. | Sistema de Cierre Pro", layout="wide")

# --- LÓGICA DE DATOS Y SESIÓN ---
if 'lista_precios' not in st.session_state:
    st.session_state.lista_precios = []
if 'fecha_vigencia' not in st.session_state:
    st.session_state.fecha_vigencia = datetime.now().strftime("%d/%m/%Y")

# --- BARRA LATERAL: CARGA Y EDICIÓN ---
with st.sidebar:
    st.header("📥 Gestión de Planilla")
    modo = st.radio("Acción:", ["Editar Precios / Manual", "Cargar Archivo .txt"])
    
    if modo == "Editar Precios / Manual":
        mod_a_editar = st.selectbox("Vehículo:", ["TERA", "VIRTUS", "T-CROSS", "NIVUS", "AMAROK", "TAOS"])
        datos_previos = next((a for a in st.session_state.lista_precios if a['Modelo'] == mod_a_editar), None)
        
        # Adjudicación por defecto según el modelo
        adj_defecto = "8, 12 y 24" if mod_a_editar in ["TERA", "NIVUS", "T-CROSS"] else ""
        if datos_previos and 'Adj_Pactada' in datos_previos: 
            adj_defecto = datos_previos['Adj_Pactada']

        with st.form("f_editar"):
            st.write(f"🔧 Ajustando valores de: **{mod_a_editar}**")
            vm = st.number_input("Valor Móvil", value=datos_previos['VM'] if datos_previos else 0, step=1)
            su = st.number_input("Suscripción", value=datos_previos['Susc'] if datos_previos else 0, step=1)
            c1 = st.number_input("Cuota 1", value=datos_previos['C1'] if datos_previos else 0, step=1)
            ad = st.number_input("Paga con Beneficio", value=datos_previos['Adh'] if datos_previos else 0, step=1)
            c2 = st.number_input("Cuota 2-13", value=datos_previos['C2_13'] if datos_previos else 0, step=1)
            cf = st.number_input("Cuota Final", value=datos_previos['CFin'] if datos_previos else 0, step=1)
            cp = st.number_input("Cuota Pura", value=datos_previos['CPura'] if datos_previos else 0, step=1)
            adj_text = st.text_input("Cuotas de Adjudicación:", value=adj_defecto)
            
            if st.form_submit_button("✅ Guardar y Actualizar"):
                nuevo = {
                    "Modelo": mod_a_editar, "VM": vm, "Susc": su, "C1": c1, 
                    "Adh": ad, "C2_13": c2, "CFin": cf, "CPura": cp, 
                    "Adj_Pactada": adj_text
                }
                st.session_state.lista_precios = [a for a in st.session_state.lista_precios if a['Modelo'] != mod_a_editar]
                st.session_state.lista_precios.append(nuevo)
                st.success(f"¡{mod_a_editar} actualizado!")
                st.rerun()
    else:
        arc = st.file_uploader("Subir .txt", type=['txt'])
        if arc:
            cont = arc.getvalue().decode("utf-8", errors="ignore")
            lineas = cont.split("\n")
            temp = []
            for l in lineas:
                if "/" in l and len(l.strip()) <= 10: st.session_state.fecha_vigencia = l.strip(); continue
                p = l.split(",")
                if len(p) >= 8:
                    try:
                        m_n = p[0].strip()
                        adj_ini = "8, 12 y 24" if m_n in ["TERA", "NIVUS", "T-CROSS"] else ""
                        temp.append({
                            "Modelo": m_n, "VM": int(float(p[1])), "Susc": int(float(p[2])), 
                            "C1": int(float(p[3])), "Adh": int(float(p[4])), "C2_13": int(float(p[5])), 
                            "CFin": int(float(p[6])), "CPura": int(float(p[7])), "Adj_Pactada": adj_ini
                        })
                    except: continue
            st.session_state.lista_precios = temp
            st.success("Planilla cargada correctamente.")

# --- CUERPO PRINCIPAL (VISTA CLIENTE) ---
if st.session_state.lista_precios:
    st.title("🚗 Arias Hnos. | Ventas")
    mod_sel = st.selectbox("🎯 Cliente interesado en:", [a['Modelo'] for a in st.session_state.lista_precios])
    d = next(a for a in st.session_state.lista_precios if a['Modelo'] == mod_sel)
    
    # Formateo
    fmt = lambda x: f"{x:,}".replace(",", ".")
    ah = (d['Susc'] + d['C1']) - d['Adh']
    
    # Lógica de planes
    if d['Modelo'] == "VIRTUS": tp = "Plan 100% financiado"
    elif d['Modelo'] in ["AMAROK", "TAOS"]: tp = "Plan 60/40"
    else: tp = "Plan 70/30"
    
    adj_final = f"🎈 *Adjudicación Pactada en Cuota:* {d['Adj_Pactada']}\\n\\n" if d.get('Adj_Pactada') else ""

    # MENSAJE FINAL CON CIERRE NEUROLINGÜÍSTICO
    msj = (f"Basada en la planilla de *Arias Hnos.* con vigencia al *{st.session_state.fecha_vigencia}*, aquí tienes el detalle de los costos para el:\\n\\n"
           f"🚘 *Vehículo:* {d['Modelo']}\\n\\n"
           f"*Valor del Auto:* ${fmt(d['VM'])}\\n"
           f"*Tipo de Plan:* {tp}\\n"
           f"*Plazo:* 84 Cuotas (Pre-cancelables a Cuota Pura hoy *${fmt(d['CPura'])}*)\\n\\n"
           f"{adj_final}"
           f"*Detalle de Inversión Inicial:*\n"
           f"* *Suscripción:* ${fmt(d['Susc'])}\\n"
           f"* *Cuota Nº 1:* ${fmt(d['C1'])}\\n"
           f"*
