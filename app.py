import streamlit as st
from datetime import datetime

# Configuración de página
st.set_page_config(page_title="Arias Hnos. | Gestión de Ventas Pro", layout="wide")

# Estilo de letra mejorado para la interfaz
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Roboto', sans-serif;
    }
    .stMarkdown h2 { color: #004a99; }
    </style>
    """, unsafe_allow_html=True)

# --- MEMORIA DE SESIÓN ---
if 'lista_precios' not in st.session_state:
    st.session_state.lista_precios = []
if 'fecha_vigencia' not in st.session_state:
    st.session_state.fecha_vigencia = datetime.now().strftime("%d/%m/%Y")

# TU PLANTILLA DE CIERRE
if 'texto_cierre' not in st.session_state:
    st.session_state.texto_cierre = (
        "💳 *DATO CLAVE:* Podés abonar el beneficio con *Tarjeta de Crédito* para patear el pago 30 días. "
        "Además, la Cuota Nº 2 recién te llegará a los *60 días*. ¡Tenés un mes de gracia para acomodar tus gastos! 🚀\n\n"
        "✨ *EL CAMBIO QUE MERECÉS:* Más allá del ahorro, imaginate lo que va a ser llegar a casa y ver la cara de orgullo "
        "de tu familia al ver el vehículo nuevo. Hoy estamos a un solo paso. 🥂\n\n"
        "⚠️ *IMPORTANTE:* Al momento de enviarte esto, solo me quedan *2 cupos disponibles* con estas condiciones. 💼✅\n\n"
        "🎁 Para asegurar la bonificación del *PRIMER SERVICIO DE MANTENIMIENTO* y el *POLARIZADO DE REGALO*, enviame ahora la foto de tu "
        "**DNI (frente y dorso)**. ¿Te parece bien? 📝📲"
    )

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("📥 Gestión de Datos")
    
    if st.session_state.lista_precios:
        modo_inicio = st.radio("Acción:", ["Usar datos guardados", "Cargar planilla nueva"], horizontal=True)
    else:
        modo_inicio = "Cargar planilla nueva"

    if modo_inicio == "Cargar planilla nueva":
        arc = st.file_uploader("Subir archivo de precios (.txt)", type=['txt'])
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
                        m_final = p[0].strip().upper()
                        # Lógica de Adjudicación Inicial con GLOBO 🎈
                        adj_ini = "8, 12 y 24" if any(x in m_final for x in ["TERA", "NIVUS", "T-CROSS", "VIRTUS"]) else ""
                        temp.append({
                            "Modelo": m_final, "VM": int(float(p[1])), "Susc": int(float(p[2])), 
                            "C1": int(float(p[3])), "Adh": int(float(p[4])), "C2_13": int(float(p[5])), 
                            "CFin": int(float(p[6])), "CPura": int(float(p[7])), "Adj_Pactada": adj_ini
                        })
                    except: continue
            st.session_state.lista_precios = temp
            st.rerun()

    if st.session_state.lista_precios:
        st.write("---")
        st.subheader("📝 Editar Cierre")
        st.session_state.texto_cierre = st.text_area("Cierre:", value=st.session_state.texto_cierre, height=250)

# --- CUERPO PRINCIPAL ---
if st.session_state.lista_precios:
    st.markdown("## 🚗 Arias Hnos. | Presupuestos Pro")
    st.markdown(f"<p style='color: gray; font-weight: bold;'>by Alejandro Scicolone | Vigencia: {st.session_state.fecha_vigencia}</p>", unsafe_allow_html=True)
    
    mod_sel = st.selectbox("🎯 Seleccione el Modelo:", [a['Modelo'] for a in st.session_state.lista_precios])
    d = next(a for a in st.session_state.lista_precios if a['Modelo'] == mod_sel)
    
    fmt = lambda x: f"{x:,}".replace(",", ".")
    costo_normal = d['Susc'] + d['C1']
    ahorro_total = costo_normal - d['Adh']
    
    # --- LÓGICA DE PLANES CORREGIDA ---
    if "VIRTUS" in d['Modelo']: 
        tp = "Plan 100% financiado"
    elif any(x in d['Modelo'] for x in ["AMAROK", "TAOS"]): 
        tp = "Plan 60/40"
    elif any(x in d['Modelo'] for x in ["TERA", "NIVUS", "T-CROSS"]): 
        tp = "Plan 70/30"
    else: 
        tp = "Plan estándar"
    
    # Uso de GLOBO 🎈
    adj_f = f"🎈 *Adjudicación Pactada en Cuota:* {d['Adj_Pactada']}\\n\\n" if d.get('Adj_Pactada') else ""
    cierre_v = st.session_state.texto_cierre.replace("\n", "\\n")
    
    msj = (f"Basada en la planilla de *Arias Hnos.* con vigencia al *{st.session_state.fecha_vigencia}*, aquí tienes el detalle de los costos para el:\\n\\n"
           f"🚘 *Vehículo:* **{d['Modelo']}**\\n\\n"
           f"*Valor del Auto:* ${fmt(d['VM'])}\\n"
           f"*Tipo de Plan:* {tp}\\n"
           f"*Plazo:* 84 Cuotas\\n\\n"
           f"{adj_f}"
           f"*Detalle de Inversión Inicial:*\\n"
           f"* *Suscripción a Financiación:* ${fmt(d['Susc'])}\\n"
           f"* *Cuota Nº 1:* ${fmt(d['C1'])}\\n"
           f"* *Costo Normal de Ingreso:* ${fmt(costo_normal)} (Ver Beneficio Exclusivo 👇)\\n\\n"
           f"-----------------------------------------------------------\\n"
           f"🔥 *BENEFICIO EXCLUSIVO:* Abonando solo **${fmt(d['Adh'])}**, ya cubrís el **INGRESO COMPLETO de Cuota 1 y Suscripción**.\\n\\n"
           f"💰 *AHORRO DIRECTO HOY: ${fmt(ahorro_total)}*\\n"
           f"-----------------------------------------------------------\\n\\n"
           f"*Esquema de cuotas posteriores:*\\n"
           f"* *Cuotas 2 a 13:* ${fmt(d['C2_13'])}\\n"
           f"* *Cuotas 14 a 84:* ${fmt(d['CFin'])}\\n"
           f"* *Cuota Pura:* ${fmt(d['CPura'])}\\n\\n"
           f"{cierre_v}")

    # BOTÓN DE COPIADO
    st.write("---")
    st.components.v1.html(f"""
    <div style="text-align: center;"><button onclick="copyToClipboard()" style="background-color: #007bff; color: white; border: none; padding: 22px; border-radius: 15px; font-weight: bold; width: 100%; font-size: 20px; cursor: pointer; box-shadow: 0px 4px 15px rgba(0,0,0,0.3); transition: 0.3s;">📋 COPIAR PARA WHATSAPP</button></div>
    <script>
    function copyToClipboard() {{
        const text = `{msj}`;
        const el = document.createElement('textarea');
        el.value = text.replace(/\\\\n/g, '\\n');
        document.body.appendChild(el);
        el.select();
        document.execCommand('copy');
        document.body.removeChild(el);
        alert('✅ ¡Presupuesto de {d['Modelo']} copiado!');
    }}
    </script>
    """, height=120)

    # VISTA PREVIA CERRADA POR DEFECTO
    with st.expander("👀 Ver vista previa del mensaje", expanded=False):
        st.markdown(msj.replace("\\n", "\n"))

else:
    st.info("👋 Hola, carga la lista de precios para empezar.")
