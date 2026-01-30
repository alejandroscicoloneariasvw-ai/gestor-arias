import streamlit as st

st.set_page_config(page_title="Arias Hnos. | Sistema de Cierre", layout="wide")

# --- MEMORIA DEL PROGRAMA ---
if 'lista_precios' not in st.session_state:
    st.session_state.lista_precios = []
if 'fecha_vigencia' not in st.session_state:
    st.session_state.fecha_vigencia = "---"

# --- MENÚ LATERAL ---
with st.sidebar:
    st.header("📂 Gestión de Datos")
    opcion = st.radio("¿Qué desea hacer?", ["Usar datos guardados", "Cargar nueva planilla"])
    
    if opcion == "Cargar nueva planilla":
        arc = st.file_uploader("Subir planilla.txt", type=['txt'])
        if arc:
            cont = arc.getvalue().decode("utf-8", errors="ignore")
            lineas = [l.strip() for l in cont.split("\n") if l.strip()]
            temp = []
            for i, l in enumerate(lineas):
                if i == 0 and "/" in l: 
                    st.session_state.fecha_vigencia = l
                    continue
                p = l.split(",")
                if len(p) >= 8:
                    try:
                        m = p[0].strip().upper()
                        adj_ini = "8, 12 y 24" if any(x in m for x in ["TERA", "NIVUS", "T-CROSS"]) else ""
                        temp.append({
                            "Modelo": m, "VM": int(float(p[1])), "Susc": int(float(p[2])), 
                            "C1": int(float(p[3])), "Adh": int(float(p[4])), "C2_13": int(float(p[5])), 
                            "CFin": int(float(p[6])), "CPura": int(float(p[7])), "Adj_Pactada": adj_ini
                        })
                    except: continue
            st.session_state.lista_precios = temp
            st.success("✅ ¡Planilla cargada!")

# --- CUERPO DEL PROGRAMA ---
if st.session_state.lista_precios:
    st.title("🚗 Arias Hnos. | Ventas")
    
    # 1. Selección del Vehículo
    mod_sel = st.selectbox("🎯 Vehículo:", [a['Modelo'] for a in st.session_state.lista_precios])
    d = next(a for a in st.session_state.lista_precios if a['Modelo'] == mod_sel)
    
    st.write("---")
    st.subheader("⚙️ Ajustes Manuales del Presupuesto")
    
    # 2. CAMPOS MANUALES (Lo que pediste modificar)
    col1, col2, col3 = st.columns(3)
    with col1:
        color_man = st.text_input("🎨 Color de unidad:", "A elección")
        entrega_man = st.number_input("💰 Valor Móvil ($):", value=int(d['VM']), step=10000)
    with col2:
        ingreso_man = st.number_input("🔥 Beneficio Ingreso ($):", value=int(d['Adh']), step=1000)
        pactada_man = st.text_input("🎈 Adjudicación Pactada:", d['Adj_Pactada'])
    with col3:
        cupos_man = st.number_input("⚠️ Cupos disponibles:", value=2, step=1)
        vendedor_man = st.text_input("👤 Vendedor:", "Alejandro")

    # Lógica de cálculos con los campos manuales
    fmt = lambda x: f"{x:,}".replace(",", ".")
    ahorro = (d['Susc'] + d['C1']) - ingreso_man
    tp = "Plan 100%" if "VIRTUS" in d['Modelo'] else ("Plan 60/40" if any(x in d['Modelo'] for x in ["AMAROK", "TAOS"]) else "Plan 70/30")
    adj_f = f"🎈 *Adjudicación Pactada en Cuota:* {pactada_man}\\n\\n" if pactada_man else ""

    # MENSAJE FINAL (Usando los datos de los campos manuales)
    msj = (f"Basada en la planilla de *Arias Hnos.* con vigencia al *{st.session_state.fecha_vigencia}*, aquí tienes el detalle de los costos para el:\\n\\n"
           f"🚘 *Vehículo:* **{d['Modelo']}**\\n"
           f"🎨 *Color:* {color_man}\\n\\n"
           f"*Valor del Auto:* ${fmt(entrega_man)}\\n"
           f"*Tipo de Plan:* {tp}\\n"
           f"*Plazo:* 84 Cuotas (Pre-cancelables a Cuota Pura hoy *${fmt(d['CPura'])}*)\\n\\n"
           f"{adj_f}"
           f"*Detalle de Inversión Inicial:*\n"
           f"* *Suscripción:* ${fmt(d['Susc'])}\\n"
           f"* *Cuota Nº 1:* ${fmt(d['C1'])}\\n"
           f"* *Costo Total de Ingreso:* ${fmt(d['Susc']+d['C1'])}.\\n\\n"
           f"-----------------------------------------------------------\\n"
           f"🔥 *BENEFICIO EXCLUSIVO:* Abonando solo **${fmt(ingreso_man)}**, ya cubrís el **INGRESO COMPLETO**. (Ahorro directo de ${fmt(ahorro)})\\n"
           f"-----------------------------------------------------------\\n\\n"
           f"💳 **DATO CLAVE:** Podés abonar el beneficio con **Tarjeta de Crédito** para patear el pago 30 días. Además, la Cuota Nº 2 recién te llegará a los **60 días**. ¡Tenés un mes de gracia para acomodar tus gastos! 🚀\\n\\n"
           f"✨ **EL CAMBIO QUE MERECÉS:** Más allá del ahorro, imaginate lo que va a ser llegar a casa y ver la cara de orgullo de tu familia al ver el **{d['Modelo']}** nuevo. Ese momento de compartirlo con amigos y disfrutar del confort que te ganaste con tu esfuerzo. Hoy estamos a un solo paso. 🥂\\n\\n"
           f"⚠️ **IMPORTANTE:** Al momento de enviarte esto, solo me quedan **{cupos_man} cupos disponibles** con estas condiciones. 💼✅\\n\\n"
           f"🎁 Para asegurarte la bonificación del **PRIMER SERVICIO DE MANTENIMIENTO** y el **POLARIZADO DE REGALO**, enviame ahora la foto de tu **DNI (frente y dorso)**. Yo reservo el cupo mientras terminás de decidirlo. ¿Te parece bien? 📝📲\\n\\n"
           f"Saluda atentamente, *{vendedor_man}*.")

    st.write("---")
    # BOTÓN DE COPIAR
    st.components.v1.html(f"""
        <button onclick="copyToClipboard()" style="background-color: #007bff; color: white; border: none; padding: 20px; border-radius: 12px; font-weight: bold; width: 100%; font-size: 18px; cursor: pointer;">📋 COPIAR PARA WHATSAPP</button>
        <script>
        function copyToClipboard() {{
            const text = `{msj}`;
            const el = document.createElement('textarea'); el.value = text;
            document.body.appendChild(el); el.select(); document.execCommand('copy'); document.body.removeChild(el);
            alert('✅ ¡Copiado!');
        }}
        </script>
    """, height=100)
    
else:
    st.info("Por favor, subí el archivo .txt en la barra lateral para activar el sistema.")
