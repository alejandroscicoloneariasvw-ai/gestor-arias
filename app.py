import streamlit as st
from datetime import datetime
import json

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Arias Hnos. | Gestión de Ventas Pro", layout="wide")

# --- ESTILOS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Segoe+UI:ital,wght@0,400;0,700;1,300&display=swap');
    html, body, [class*="css"], .stTextArea textarea { font-family: 'Segoe UI', sans-serif !important; font-size: 15px !important; }
    .firma-scicolone { font-style: italic; font-weight: 300; font-size: 14px; color: #6c757d; margin-top: -15px; margin-bottom: 20px; }
    .caja-previa { background-color: #ffffff; padding: 25px; border-radius: 12px; border: 1px solid #e0e0e0; }
    </style>
    """, unsafe_allow_html=True)

if 'lista_precios' not in st.session_state:
    st.session_state.lista_precios = []
if 'fecha_vigencia' not in st.session_state:
    st.session_state.fecha_vigencia = datetime.now().strftime("%d/%m/%Y")

if 'texto_cierre' not in st.session_state:
    st.session_state.texto_cierre = (
        "💳 *DATO CLAVE:* Podés abonar el beneficio con *Tarjeta de Crédito* para patear el pago 30 días. "
        "Además, la Cuota Nº 2 recién te llegará a los *60 días*. ¡Tenés un mes de gracia para acomodar tus gastos! 🚀\n\n"
        "✨ *EL CAMBIO QUE MERECÉS:* Imaginate lo que va a ser llegar a casa y ver la cara de orgullo "
        "de tu familia al ver el vehículo nuevo. Hoy estamos a un solo paso. 🥂\n\n"
        "⚠️ *IMPORTANTE:* Al momento de enviarte esto, solo me quedan *2 cupos disponibles* con estas condiciones "
        "de abonar un monto menor en la Cuota 1 y Suscripción (Ver Beneficio Exclusivo arriba). 💼✅\n\n"
        "🎁 Para asegurar la bonificación del *PRIMER SERVICIO DE MANTENIMIENTO* y el *POLARIZADO DE REGALO*, enviame ahora la foto de tu "
        "**DNI (frente y dorso)**. Yo reservo el cupo mientras terminás de decidirlo. ¡Arrancá tu nuevo auto! 🚙🏁🏆✅ ¿Te parece bien? 📝📲"
    )

with st.sidebar:
    st.header("📥 Gestión de Datos")
    modo = st.radio("Acción:", ["Usar datos guardados", "Cargar planilla nueva"], horizontal=True) if st.session_state.lista_precios else "Cargar planilla nueva"
    
    if modo == "Cargar planilla nueva":
        arc = st.file_uploader("Subir planilla .txt", type=['txt'])
        if arc:
            cont = arc.getvalue().decode("utf-8", errors="ignore")
            lineas = cont.split("\n")
            temp = []
            for l in lineas:
                if "/" in l and len(l.strip()) <= 10: 
                    st.session_state.fecha_vigencia = l.strip()
                    continue
                p = l.split(",")
                if len(p) >= 8:
                    try:
                        modelo_nombre = p[0].strip().upper()
                        # Lógica: Solo ciertos modelos tienen adjudicación pactada
                        tiene_adj = not any(x in modelo_nombre for x in ["VIRTUS", "AMAROK", "TAOS"])
                        temp.append({
                            "Modelo": modelo_nombre, "VM": int(float(p[1])), "Susc": int(float(p[2])), 
                            "C1": int(float(p[3])), "Adh": int(float(p[4])), "C2_13": int(float(p[5])), 
                            "CFin": int(float(p[6])), "CPura": int(float(p[7])),
                            "Adj": "8, 12 y 24" if tiene_adj else ""
                        })
                    except: continue
            st.session_state.lista_precios = temp
            st.rerun()
    
    if st.session_state.lista_precios:
        st.write("---")
        st.subheader("💰 Editar Todas las Variables")
        m_sel_e = st.selectbox("Modelo a editar:", [a['Modelo'] for a in st.session_state.lista_precios])
        d_e = next(a for a in st.session_state.lista_precios if a['Modelo'] == m_sel_e)

        with st.form("f_edit_total"):
            c_vm = st.number_input("Valor de la Unidad ($):", value=int(d_e['VM']))
            c_su = st.number_input("Suscripción a Financiación ($):", value=int(d_e['Susc']))
            c_c1 = st.number_input("Cuota Nº 1 ($):", value=int(d_e['C1']))
            c_ad = st.number_input("Beneficio / Adhesión ($):", value=int(d_e['Adh']))
            c_c2 = st.number_input("Cuotas 2 a 13 ($):", value=int(d_e['C2_13']))
            c_cf = st.number_input("Cuotas 14 a 84 ($):", value=int(d_e['CFin']))
            c_cp = st.number_input("Cuota Pura ($):", value=int(d_e['CPura']))
            c_adj = st.text_input("Adjudicación Pactada (dejar vacío si no tiene):", value=d_e.get('Adj', ''))
            
            if st.form_submit_button("💾 Guardar Cambios"):
                for item in st.session_state.lista_precios:
                    if item['Modelo'] == m_sel_e:
                        item.update({
                            "VM": c_vm, "Susc": c_su, "C1": c_c1, "Adh": c_ad, 
                            "C2_13": c_c2, "CFin": c_cf, "CPura": c_cp, "Adj": c_adj
                        })
                st.rerun()

if st.session_state.lista_precios:
    st.markdown("### 🚗 Arias Hnos. | Gestión de Presupuestos")
    st.markdown(f'<div class="firma-scicolone">by Alejandro Scicolone</div>', unsafe_allow_html=True)
    mod_sel = st.selectbox("🎯 Seleccioná el Modelo:", [a['Modelo'] for a in st.session_state.lista_precios])
    d = next(a for a in st.session_state.lista_precios if a['Modelo'] == mod_sel)
    fmt = lambda x: f"{x:,}".replace(",", ".")
    
    atencion = "💎 *¡ATENCIÓN!*"
    if "VIRTUS" in d['Modelo']:
        encabezado = f"{atencion} **Vehículo financiado 100% en cuotas sin necesidad de integración mínima.**"
        tp, porc, alic_h = "Plan 100% financiado", "0%", 0
    elif any(x in d['Modelo'] for x in ["AMAROK", "TAOS"]):
        encabezado = f"{atencion} **Financiá el 60% de tu unidad en cuotas y adjudicalo con el 40% de su valor.**"
        tp, porc, alic_h = "Plan 60/40", "40%", int(d['VM'] * 0.4)
    else:
        encabezado = f"{atencion} **Financiá el 70% de tu unidad en cuotas y adjudicalo con el 30% de su valor.**"
        tp, porc, alic_h = "Plan 70/30", "30%", int(d['VM'] * 0.3)

    # Lógica de la línea de adjudicación en el mensaje
    linea_adj = f"🎈 *Adjudicación Pactada en Cuota:* {d['Adj']}\n\n" if d.get('Adj') else ""

    costo_normal = d['Susc'] + d['C1']
    ahorro_total = costo_normal - d['Adh']
    alic_line = f"* Alícuota ({porc}): Hoy ${fmt(alic_h)}\n" if alic_h > 0 else ""
    
    msj = (f"{encabezado}\n\n"
            f"Basada en la planilla de *Arias Hnos.* con vigencia al **{st.session_state.fecha_vigencia}**, aquí tienes el detalle de los costos para el:\n\n"
            f"🚘 **Vehículo:** **{d['Modelo']}**\n"
            f"* **Valor de la Unidad:** ${fmt(d['VM'])}\n"
            f"* **Tipo de Plan:** {tp}\n"
            f"* **Plazo:** 84 Cuotas (Pre-cancelables a Cuota Pura)\n\n"
            f"{linea_adj}"
            f"**Detalle de Inversión Inicial:**\n"
            f"* Suscripción a Financiación: ${fmt(d['Susc'])}\n"
            f"* Cuota Nº 1: ${fmt(d['C1'])}\n"
            f"* **Costo Normal de Ingreso:** ${fmt(costo_normal)} (Ver Beneficio Exclusivo 👇)\n\n"
            f"🔥 **BENEFICIO EXCLUSIVO:** Abonando solo **${fmt(d['Adh'])}**, ya cubrís el **INGRESO COMPLETO de Cuota 1 y Suscripción**.\n"
            f"💰 **AHORRO DIRECTO HOY: ${fmt(ahorro_total)}**\n"
            f"-----------------------------------------------------------\n\n"
            f"**Esquema de cuotas posteriores:**\n"
            f"* Cuotas 2 a 13: ${fmt(d['C2_13'])}\n"
            f"* Cuotas 14 a 84: ${fmt(d['CFin'])}\n"
            f"{alic_line}"
            f"* Cuota Pura: ${fmt(d['CPura'])}\n\n"
            f"{st.session_state.texto_cierre}")

    js_msg = json.dumps(msj)

    st.components.v1.html(f"""
    <button onclick="copyToClipboard()" style="background-color: #007bff; color: white; border: none; padding: 15px; border-radius: 10px; font-weight: bold; width: 100%; font-size: 18px; cursor: pointer;">
        📋 COPIAR PARA WHATSAPP
    </button>
    <script>
    function copyToClipboard() {{
        const text = {js_msg};
        const el = document.createElement('textarea');
        el.value = text;
        document.body.appendChild(el);
        el.select();
        document.execCommand('copy');
        document.body.removeChild(el);
        alert('✅ ¡Copiado con éxito!');
    }}
    </script>
    """, height=80)
    
    with st.expander("👀 Ver Vista Previa", expanded=True):
        st.markdown(f'<div class="caja-previa">{msj.replace("\n", "<br>").replace("**", "<b>").replace("*", "")}</div>', unsafe_allow_html=True)
else:
    st.info("👋 Hola, cargá la lista de precios para empezar.")
