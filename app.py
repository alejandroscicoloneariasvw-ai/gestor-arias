import streamlit as st

st.set_page_config(page_title="Arias Hnos. | Sistema de Cierre", layout="wide")

# --- MEMORIA DEL PROGRAMA ---
if 'lista_precios' not in st.session_state:
    st.session_state.lista_precios = []
if 'fecha_vigencia' not in st.session_state:
    st.session_state.fecha_vigencia = "---"

# --- PANEL LATERAL: CARGA ---
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
                        temp.append({
                            "Modelo": m, "VM": int(float(p[1])), "Susc": int(float(p[2])), 
                            "C1": int(float(p[3])), "Adh": int(float(p[4])), "C2_13": int(float(p[5])), 
                            "CFin": int(float(p[6])), "CPura": int(float(p[7]))
                        })
                    except: continue
            st.session_state.lista_precios = temp
            st.success("✅ Planilla cargada")

# --- CUERPO PRINCIPAL ---
if st.session_state.lista_precios:
    st.title("🚗 Arias Hnos. | Ventas")
    
    # 1. Selección del Vehículo
    mod_sel = st.selectbox("🎯 Seleccione el Vehículo:", [a['Modelo'] for a in st.session_state.lista_precios])
    d = next(a for a in st.session_state.lista_precios if a['Modelo'] == mod_sel)
    
    st.write("---")
    st.subheader("📝 Campos de la Planilla (Edición Manual)")
    
    # 2. CAMPOS DE EDICIÓN (Todo lo referente a la planilla)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        vm_m = st.number_input("Valor Móvil ($):", value=int(d['VM']))
        susc_m = st.number_input("Suscripción ($):", value=int(d['Susc']))
    with c2:
        c1_m = st.number_input("Cuota Nº 1 ($):", value=int(d['C1']))
        adh_m = st.number_input("Beneficio/Adhesión ($):", value=int(d['Adh']))
    with c3:
        cpura_m = st.number_input("Cuota Pura ($):", value=int(d['CPura']))
        c2_13_m = st.number_input("Cuota 2 a 13 ($):", value=int(d['C2_13']))
    with c4:
        cupos_m = st.number_input("Cupos:", value=2)
        color_m = st.text_input("Color:", "A elección")

    # Campos de Texto Adicionales
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        adj_m = st.text_input("Adjudicación Pactada:", "8, 12 y 24")
    with col_t2:
        vend_m = st.text_input("Vendedor:", "Alejandro")

    # Cálculos dinámicos
    fmt = lambda x: f"{x:,}".replace(",", ".")
    ahorro = (susc_m + c1_m) - adh_m
    tp = "Plan 100%" if "VIRTUS" in mod_sel else ("Plan 60/40" if any(x in mod_sel for x in ["AMAROK", "TAOS"]) else "Plan 70/30")
    adj_txt = f"🎈 *Adjudicación Pactada en Cuota:* {adj_m}\\n\\n" if adj_m else ""

    # MENSAJE FINAL (El que funcionaba fantástico)
    msj = (f"Basada en la planilla de *Arias Hnos.* con vigencia al *{st.session_state.fecha_vigencia}*, aquí tienes el detalle para el:\\n\\n"
           f"🚘 *Vehículo:* **{mod_sel}**\\n"
           f"🎨 *Color:* {color_m}\\n\\n"
           f"*Valor del Auto:* ${fmt(vm_m)}\\n"
           f"*Tipo de Plan:* {tp}\\n"
           f"*Plazo:* 84 Cuotas (Pre-cancelables a Cuota Pura hoy *${fmt(cpura_m)}*)\\n\\n"
           f"{adj_txt}"
           f"*Detalle de Inversión Inicial:*\n"
           f"* *Suscripción:* ${fmt(susc_m)}\\n"
           f"* *Cuota Nº 1:* ${fmt(c1_m)}\\n"
           f"* *Costo Total de Ingreso:* ${fmt(susc_m + c1_m)}.\\n\\n"
           f"-----------------------------------------------------------\\n"
           f"🔥 *BENEFICIO EXCLUSIVO:* Abonando solo **${fmt(adh_m)}**, ya cubrís el **INGRESO COMPLETO**. (Ahorro directo de ${fmt(ahorro)})\\n"
           f"-----------------------------------------------------------\\n\\n"
           f"💳 **DATO CLAVE:** Podés abonar el beneficio con **Tarjeta de Crédito** para patear el pago 30 días. Además, la Cuota Nº 2 recién te llegará a los **60 días**. 🚀\\n\\n"
           f"✨ **EL CAMBIO QUE MERECÉS:** Imaginate lo que va a ser llegar a casa y ver la cara de orgullo de tu familia al ver el **{mod_sel}** nuevo. Hoy estamos a un solo paso. 🥂\\n\\n"
           f"⚠️ **IMPORTANTE:** Me quedan **{cupos_m} cupos disponibles** con estas condiciones. 💼✅\\n\\n"
           f"🎁 Para asegurar la bonificación del **PRIMER SERVICIO** y el **POLARIZADO**, enviame ahora la foto de tu **DNI**. Yo reservo el cupo. ¿Te parece bien? 📝📲\\n\\n"
           f"Saluda atentamente, *{vend_m}*.")

    st.write("---")
    # BOTÓN DE COPIAR (Tu botón azul)
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
    st.info("Por favor, cargue la planilla en el menú lateral para empezar.")
