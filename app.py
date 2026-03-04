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
    st.session_state.fecha_vigencia = "03/03/2026"

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
                            "CFin": int(float(p[6])), "CPura": int(float(p[7])), "Adj_Pactada": adj_ini
                        })
                    except: continue
            st.session_state.lista_precios = temp
            st.rerun()

    if st.session_state.lista_precios:
        st.write("---")
        st.subheader("💰 Modificar Precios")
        opcs = [a['Modelo'] for a in st.session_state.lista_precios]
        m_sel_e = st.selectbox("Seleccionar Modelo para editar:", opcs)
        d_e = next(a for a in st.session_state.lista_precios if a['Modelo'] == m_sel_e)

        with st.form("f_edit_precios"):
            n_nom = st.text_input("Nombre:", value=d_e['Modelo'])
            n_vm = st.number_input("Valor Móvil ($):", value=int(d_e['VM']))
            n_su = st.number_input("Suscripción ($):", value=int(d_e['Susc']))
            n_c1 = st.number_input("Cuota 1 ($):", value=int(d_e['C1']))
            n_ad = st.number_input("Beneficio ($):", value=int(d_e['Adh']))
            n_c2 = st.number_input("Cuotas 2 a 13 ($):", value=int(d_e['C2_13']))
            n_cf = st.number_input("Cuotas 14 a 84 ($):", value=int(d_e['CFin']))
            n_cp = st.number_input("Cuota Pura ($):", value=int(d_e['CPura']))
            n_adj = st.text_input("Adjudicación Pactada:", value=d_e['Adj_Pactada'])
            if st.form_submit_button("💾 Guardar Cambios"):
                for item in st.session_state.lista_precios:
                    if item['Modelo'] == m_sel_e:
                        item.update({"Modelo": n_nom.upper(), "VM": n_vm, "Susc": n_su, "C1": n_c1, "Adh": n_ad, "C2_13": n_c2, "CFin": n_cf, "CPura": n_cp, "Adj_Pactada": n_adj})
                st.rerun()

# --- CUERPO PRINCIPAL ---
if st.session_state.lista_precios:
    st.markdown("### 🚗 Arias Hnos. | Gestión de Presupuestos")
    st.markdown(f'<div class="firma-scicolone">by Alejandro Scicolone</div>', unsafe_allow_html=True)
    
    mod_sel = st.selectbox("🎯 Modelo para el cliente:", [a['Modelo'] for a in st.session_state.lista_precios])
    d = next(a for a in st.session_state.lista_precios if a['Modelo'] == mod_sel)
    
    fmt = lambda x: f"{x:,}".replace(",", ".")
    costo_normal = d['Susc'] + d['C1']
    ahorro_total = costo_normal - d['Adh']
    
    encabezado_plan = ""
    if "VIRTUS" in d['Modelo']: 
        tp = "Plan 100% financiado"
        alicuota_txt = ""
    elif any(x in d['Modelo'] for x in ["AMAROK", "TAOS"]): 
        tp = "Plan 60/40"
        encabezado_plan = f"Financia hasta el **60%** de tu unidad en cuotas y adjudicalo con el **40%** de su valor.\\n\\n"
        monto_ali = d['VM'] * 0.40
        alicuota_txt = f"* *Alícuota Extraordinaria (40%):* ${fmt(int(monto_ali))} (Se abona al adjudicar)\\n"
    elif any(x in d['Modelo'] for x in ["TERA", "NIVUS", "T-CROSS"]): 
        tp = "Plan 70/30"
        encabezado_plan = f"Financia hasta el **70%** de tu unidad en cuotas y adjudicalo con el **30%** de su valor.\\n\\n"
        monto_ali = d['VM'] * 0.30
        alicuota_txt = f"* *Alícuota Extraordinaria (30%):* ${fmt(int(monto_ali))} (Se abona al adjudicar)\\n"
    else: 
        tp = "Plan estándar"
        alicuota_txt = ""

    adj_f = f"🎈 **Adjudicación Pactada en Cuota:** {d['Adj_Pactada']}\\n\\n" if d.get('Adj_Pactada') and d['Adj_Pactada'].strip() != "" else ""
    cierre_v = st.session_state.texto_cierre.replace("\\n", "\\\\n")
    
    msj = (f"Basada en la planilla de *Arias Hnos.* con vigencia al **{st.session_state.fecha_vigencia}**, aquí tienes el detalle de los costos para el:\\\\n\\\\n"
           f"{encabezado_plan}"
           f"🚘 **Vehículo:** **{d['Modelo']}**\\\\n\\\\n"
           f"**Valor del Auto:** ${fmt(d['VM'])}\\\\n"
           f"**Tipo de Plan:** {tp}\\\\n"
           f"**Plazo:** 84 Cuotas (Pre-cancelables a Cuota Pura)\\\\n\\\\n"
           f"{adj_f}"
           f"**Detalle de Inversión Inicial:**\\\\n"
           f"* *Suscripción a Financiación:* ${fmt(d['Susc'])}\\\\n"
           f"* *Cuota Nº 1:* ${fmt(d['C1'])}\\\\n"
           f"* **Costo Normal de Ingreso:** ${fmt(costo_normal)} (Ver Beneficio Exclusivo 👇)\\\\n\\\\n"
           f"-----------------------------------------------------------\\\\n"
           f"🔥 **BENEFICIO EXCLUSIVO:** Abonando solo **${fmt(d['Adh'])}**, ya cubrís el **INGRESO COMPLETO de Cuota 1 y Suscripción**.\\\\n\\\\n"
           f"💰 **AHORRO DIRECTO HOY: ${fmt(ahorro_total)}**\\\\n"
           f"-----------------------------------------------------------\\\\n\\\\n"
           f"**Esquema de cuotas posteriores:**\\\\n"
           f"* *Cuotas 2 a 13:* ${fmt(d['C2_13'])}\\\\n"
           f"* *Cuotas 14 a 84:* ${fmt(d['CFin'])}\\\\n"
           f"* *Cuota Pura:* ${fmt(d['CPura'])}\\\\n"
           f"{alicuota_txt}\\\\n"
           f"{cierre_v}")

    st.components.v1.html(f"""
    <div style="text-align: center;">
        <button onclick="copyToClipboard()" style="background-color: #007bff; color: white; border: none; padding: 20px; border-radius: 12px; font-weight: bold; width: 100%; font-size: 18px; cursor: pointer;">📋 COPIAR PARA WHATSAPP</button>
    </div>
    <script>
    function copyToClipboard() {{
        const text = `{msj}`;
        const el = document.createElement('textarea');
        el.value = text.replace(/\\\\\\\\n/g, '\\n');
        document.body.appendChild(el);
        el.select();
        document.execCommand('copy');
        document.body.removeChild(el);
        alert('✅ ¡Copiado con éxito!');
    }}
    </script>
    """, height=100)

    with st.expander("👀 Ver Vista Previa del Mensaje", expanded=False):
        vista_html = msj.replace("\\\\\\\\n", "<br>").replace("**", "<b>").replace("*", "")
        st.markdown(f'<div class="caja-previa">{vista_html}</div>', unsafe_allow_html=True)
else:
    st.info("👋 Hola, carga la lista de precios para empezar.")
