import streamlit as st
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Arias Hnos. | Gestión de Ventas Pro", layout="wide")

# --- ESTILOS UNIFICADOS (BY ALEJANDRO) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Segoe+UI:ital,wght@0,400;0,700;1,300&display=swap');
    html, body, [class*="css"], .stTextArea textarea { font-family: 'Segoe UI', sans-serif !important; font-size: 15px !important; }
    .firma-scicolone { font-style: italic; font-weight: 300; font-size: 14px; color: #6c757d; margin-top: -15px; margin-bottom: 20px; }
    .caja-previa { background-color: #ffffff; padding: 25px; border-radius: 12px; border: 1px solid #e0e0e0; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- MEMORIA DE SESIÓN ---
if 'lista_precios' not in st.session_state:
    st.session_state.lista_precios = []
if 'fecha_vigencia' not in st.session_state:
    st.session_state.fecha_vigencia = datetime.now().strftime("%d/%m/%Y")

# --- TEXTO DE CIERRE CON NEUROVENTAS ---
if 'texto_cierre' not in st.session_state:
    st.session_state.texto_cierre = (
        "💳 *DATO CLAVE:* Podés abonar el beneficio con *Tarjeta de Crédito* para patear el pago 30 días. "
        "Además, la Cuota Nº 2 recién te llegará a los *60 días*. ¡Tenés un mes de gracia para acomodar tus gastos! 🚀\\n\\n"
        "✨ *EL CAMBIO QUE MERECÉS:* Imaginate lo que va a ser llegar a casa y ver la cara de orgullo "
        "de tu familia al ver el vehículo nuevo. Hoy estamos a un solo paso. 🥂\\n\\n"
        "⚠️ *IMPORTANTE:* Al momento de enviarte esto, solo me quedan *2 cupos disponibles* con estas condiciones. 💼✅\\n\\n"
        "🎁 Para asegurar la bonificación del *PRIMER SERVICIO DE MANTENIMIENTO* y el *POLARIZADO DE REGALO*, enviame ahora la foto de tu "
        "**DNI (frente y dorso)**. Yo reservo el cupo mientras terminás de decidirlo. ¡Arrancá tu nuevo auto! 🚙🏁🏆✅ ¿Te parece bien? 📝📲"
    )

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("📥 Gestión de Datos")
    # Pregunta si usar guardados o cargar nueva (Tu pedido)
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
                        temp.append({
                            "Modelo": p[0].strip().upper(), "VM": int(float(p[1])), "Susc": int(float(p[2])), 
                            "C1": int(float(p[3])), "Adh": int(float(p[4])), "C2_13": int(float(p[5])), 
                            "CFin": int(float(p[6])), "CPura": int(float(p[7]))
                        })
                    except: continue
            st.session_state.lista_precios = temp
            st.rerun()
    
    if st.session_state.lista_precios:
        st.write("---")
        st.session_state.texto_cierre = st.text_area("📝 Modificar Cierre:", value=st.session_state.texto_cierre, height=250)

# --- CUERPO PRINCIPAL ---
if st.session_state.lista_precios:
    st.markdown("### 🚗 Arias Hnos. | Gestión de Presupuestos")
    st.markdown(f'<div class="firma-scicolone">by Alejandro Scicolone</div>', unsafe_allow_html=True)
    
    mod_sel = st.selectbox("🎯 Seleccioná el Modelo:", [a['Modelo'] for a in st.session_state.lista_precios])
    d = next(a for a in st.session_state.lista_precios if a['Modelo'] == mod_sel)
    
    fmt = lambda x: f"{x:,}".replace(",", ".")
    costo_normal = d['Susc'] + d['C1']
    ahorro_total = costo_normal - d['Adh']
    
    # Lógica de planes y encabezado (Perfeccionada)
    if "VIRTUS" in d['Modelo']:
        encabezado = "**Vehículo financiado 100% en cuotas sin necesidad de integración mínima.**"
        tp = "Plan 100% financiado"
        alic_line = ""
    elif any(x in d['Modelo'] for x in ["AMAROK", "TAOS"]):
        encabezado = "**Financiá el 60% de tu unidad en cuotas y adjudicalo con el 40% de su valor.**"
        tp = "Plan 60/40"
        alic_line = f"* Alícuota (40%): **Hoy ${fmt(int(d['VM']*0.4))}**\\n"
    else:
        encabezado = "**Financiá el 70% de tu unidad en cuotas y adjudicalo con el 30% de su valor.**"
        tp = "Plan 70/30"
        alic_line = f"* Alícuota (30%): **Hoy ${fmt(int(d['VM']*0.3))}**\\n"

    cierre_v = st.session_state.texto_cierre.replace("\n", "\\n")
    
    # Construcción del Mensaje (Encabezado arriba de todo)
    msj = (f"{encabezado}\\n\\n"
            f"Presupuesto de *Arias Hnos.* con vigencia al **{st.session_state.fecha_vigencia}** para el:\\n\\n"
            f"🚘 **Vehículo:** **{d['Modelo']}**\\n"
            f"**Valor del Auto:** ${fmt(d['VM'])}\\n"
            f"**Tipo de Plan:** {tp}\\n\\n"
            f"**Detalle de Inversión Inicial:**\\n"
            f"* Suscripción: ${fmt(d['Susc'])}\\n"
            f"* Cuota Nº 1: ${fmt(d['C1'])}\\n"
            f"* **Costo Normal de Ingreso:** ${fmt(costo_normal)}\\n\\n"
            f"-----------------------------------------------------------\\n"
            f"🔥 **BENEFICIO EXCLUSIVO:** Abonando solo **${fmt(d['Adh'])}**, ya cubrís el **INGRESO COMPLETO de Cuota 1 y Suscripción**.\\n"
            f"💰 **AHORRO DIRECTO HOY: ${fmt(ahorro_total)}**\\n"
            f"-----------------------------------------------------------\\n\\n"
            f"**Esquema de cuotas posteriores:**\\n"
            f"* Cuotas 2 a 13: ${fmt(d['C2_13'])}\\n"
            f"* Cuotas 14 a 84: ${fmt(d['CFin'])}\\n"
            f"{alic_line}"
            f"* Cuota Pura: ${fmt(d['CPura'])}\\n\\n"
            f"{cierre_v}")

    # BOTÓN DE COPIADO
    st.components.v1.html(f"""
    <button onclick="copyToClipboard()" style="background-color: #007bff; color: white; border: none; padding: 15px; border-radius: 10px; font-weight: bold; width: 100%; font-size: 18px; cursor: pointer;">
        📋 COPIAR PARA WHATSAPP
    </button>
    <script>
    function copyToClipboard() {{
        const text = `{msj}`;
        const el = document.createElement('textarea');
        el.value = text.replace(/\\\\n/g, '\\n');
        document.body.appendChild(el);
        el.select();
        document.execCommand('copy');
        document.body.removeChild(el);
        alert('✅ ¡Copiado con éxito, Alejandro!');
    }}
    </script>
    """, height=80)

    with st.expander("👀 Vista Previa del Mensaje"):
        st.markdown(f'<div class="caja-previa">{msj.replace("\\n", "<br>").replace("**", "<b>").replace("*", "")}</div>', unsafe_allow_html=True)
else:
    st.info("👋 Hola Alejandro, cargá la lista de precios en el menú de la izquierda para empezar.")
