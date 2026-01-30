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
    # Pregunta si quiere cargar o usar lo viejo
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
    else:
        if not st.session_state.lista_precios:
            st.warning("⚠️ No hay datos previos. Por favor, cargue una planilla primero.")

# --- CUERPO DEL PROGRAMA ---
if st.session_state.lista_precios:
    st.title("🚗 Arias Hnos. | Ventas")
    mod_sel = st.selectbox("🎯 Vehículo:", [a['Modelo'] for a in st.session_state.lista_precios])
    d = next(a for a in st.session_state.lista_precios if a['Modelo'] == mod_sel)
    
    fmt = lambda x: f"{x:,}".replace(",", ".")
    ah = (d['Susc'] + d['C1']) - d['Adh']
    tp = "Plan 100%" if "VIRTUS" in d['Modelo'] else ("Plan 60/40" if any(x in d['Modelo'] for x in ["AMAROK", "TAOS"]) else "Plan 70/30")
    adj_f = f"🎈 *Adjudicación Pactada en Cuota:* {d['Adj_Pactada']}\\n\\n" if d['Adj_Pactada'] else ""

    # TU MENSAJE DE VENTAS ORIGINAL
    msj = (f"Basada en la planilla de *Arias Hnos.* con vigencia al *{st.session_state.fecha_vigencia}*, aquí tienes el detalle de los costos para el:\\n\\n"
           f"🚘 *Vehículo:* **{d['Modelo']}**\\n\\n"
           f"*Valor del Auto:* ${fmt(d['VM'])}\\n"
           f"*Tipo de Plan:* {tp}\\n"
           f"*Plazo:* 84 Cuotas (Pre-cancelables a Cuota Pura hoy *${fmt(d['CPura'])}*)\\n\\n"
           f"{adj_f}"
           f"*Detalle de Inversión Inicial:*\n"
           f"* *Suscripción:* ${fmt(d['Susc'])}\\n"
           f"* *Cuota Nº 1:* ${fmt(d['C1'])}\\n"
           f"* *Costo Total de Ingreso:* ${fmt(d['Susc']+d['C1'])}.\\n\\n"
           f"-----------------------------------------------------------\\n"
           f"🔥 *BENEFICIO EXCLUSIVO:* Abonando solo **${fmt(d['Adh'])}**, ya cubrís el **INGRESO COMPLETO**. (Ahorro directo de ${fmt(ah)})\\n"
           f"-----------------------------------------------------------\\n\\n"
           f"💳 **DATO CLAVE:** Podés abonar el beneficio con **Tarjeta de Crédito** para patear el pago 30 días. Además, la Cuota Nº 2 recién te llegará a los **60 días**. ¡Tenés un mes de gracia para acomodar tus gastos! 🚀\\n\\n"
           f"✨ **EL CAMBIO QUE MERECÉS:** Más allá del ahorro, imaginate lo que va a ser llegar a casa y ver la cara de orgullo de tu familia al ver el **{d['Modelo']}** nuevo. Ese momento de compartirlo con amigos y disfrutar del confort que te ganaste con tu esfuerzo. Hoy estamos a un solo paso. 🥂\\n\\n"
           f"⚠️ **IMPORTANTE:** Al momento de enviarte esto, solo me quedan **2 cupos disponibles** con estas condiciones de abonar un monto menor en la Cuota 1 y Suscripción (Ver **Beneficio Exclusivo** arriba). 💼✅\\n\\n"
           f"🎁 Para asegurarte la bonificación del **PRIMER SERVICIO DE MANTENIMIENTO** y el **POLARIZADO DE REGALO**, enviame ahora la foto de tu **DNI (frente y dorso)**. Yo reservo el cupo mientras terminás de decidirlo, así no perdés el beneficio por falta de stock y coordinamos el pago del beneficio. ¿Te parece bien? 📝📲")

    st.write("---")
    # BOTÓN DE COPIAR (Tu botón azul grande)
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
    
    if st.button("🖨️ IMPRIMIR"):
        st.write("Generando versión para imprimir...")
else:
    st.info("Por favor, subí el archivo .txt en la barra lateral para activar el sistema.")
