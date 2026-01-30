import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Arias Hnos. | Gestión de Ventas Pro", layout="wide")

# --- LÓGICA DE DATOS Y SESIÓN ---
if 'lista_precios' not in st.session_state:
    st.session_state.lista_precios = []
if 'fecha_vigencia' not in st.session_state:
    st.session_state.fecha_vigencia = datetime.now().strftime("%d/%m/%Y")

# --- BARRA LATERAL: CARGA Y EDICIÓN ---
with st.sidebar:
    st.header("📥 Carga y Edición")
    modo = st.radio("Método:", ["Manual / Editar", "Subir Archivo (.txt)"])
    
    if modo == "Manual / Editar":
        opciones_actuales = [a['Modelo'] for a in st.session_state.lista_precios] if st.session_state.lista_precios else ["TERA", "VIRTUS", "T-CROSS", "NIVUS", "AMAROK", "TAOS"]
        mod_a_editar = st.selectbox("Modelo a modificar:", opciones_actuales)
        
        datos_previos = next((a for a in st.session_state.lista_precios if a['Modelo'] == mod_a_editar), None)

        with st.form("f_editar"):
            st.write(f"Editing: **{mod_a_editar}**")
            nuevo_nombre = st.text_input("Nombre del Vehículo (Completo):", value=mod_a_editar)
            vm = st.number_input("Valor Móvil", value=int(datos_previos['VM']) if datos_previos else 0, step=1)
            su = st.number_input("Suscripción", value=int(datos_previos['Susc']) if datos_previos else 0, step=1)
            c1 = st.number_input("Cuota 1", value=int(datos_previos['C1']) if datos_previos else 0, step=1)
            ad = st.number_input("Paga con Beneficio", value=int(datos_previos['Adh']) if datos_previos else 0, step=1)
            c2 = st.number_input("Cuota 2-13", value=int(datos_previos['C2_13']) if datos_previos else 0, step=1)
            cf = st.number_input("Cuota Final", value=int(datos_previos['CFin']) if datos_previos else 0, step=1)
            cp = st.number_input("Cuota Pura", value=int(datos_previos['CPura']) if datos_previos else 0, step=1)
            adj_text = st.text_input("Cuotas de Adjudicación:", value=datos_previos['Adj_Pactada'] if datos_previos else "8, 12 y 24")
            
            if st.form_submit_button("✅ Guardar y Actualizar"):
                nuevo = {"Modelo": nuevo_nombre.upper(), "VM": vm, "Susc": su, "C1": c1, "Adh": ad, "C2_13": c2, "CFin": cf, "CPura": cp, "Adj_Pactada": adj_text}
                st.session_state.lista_precios = [a for a in st.session_state.lista_precios if a['Modelo'] != mod_a_editar]
                st.session_state.lista_precios.append(nuevo)
                st.success("¡Datos actualizados!")
                st.rerun()
    else:
        arc = st.file_uploader("Subir .txt", type=['txt'])
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
                        adj_ini = "8, 12 y 24" if any(x in m_final for x in ["TERA", "NIVUS", "T-CROSS"]) else ""
                        temp.append({
                            "Modelo": m_final, "VM": int(float(p[1])), "Susc": int(float(p[2])), 
                            "C1": int(float(p[3])), "Adh": int(float(p[4])), "C2_13": int(float(p[5])), 
                            "CFin": int(float(p[6])), "CPura": int(float(p[7])), "Adj_Pactada": adj_ini
                        })
                    except: continue
            st.session_state.lista_precios = temp
            st.success("Planilla cargada correctamente.")

# --- CUERPO PRINCIPAL ---
if st.session_state.lista_precios:
    # EL CAMBIO QUE PEDISTE: Título y firma personalizada
    st.markdown("## 🚗 Arias Hnos. | Presupuestos")
    st.markdown("<p style='font-size: 14px; margin-top: -15px;'>by Alejandro Scicolone</p>", unsafe_allow_html=True)
    
    mod_sel = st.selectbox("🎯 Cliente interesado en:", [a['Modelo'] for a in st.session_state.lista_precios])
    d = next(a for a in st.session_state.lista_precios if a['Modelo'] == mod_sel)
    
    fmt = lambda x: f"{x:,}".replace(",", ".")
    ah = (d['Susc'] + d['C1']) - d['Adh']
    
    if "VIRTUS" in d['Modelo']: tp = "Plan 100% financiado"
    elif "AMAROK" in d['Modelo'] or "TAOS" in d['Modelo']: tp = "Plan 60/40"
    else: tp = "Plan 70/30"
    
    adj_final = f"🎈 *Adjudicación Pactada en Cuota:* {d['Adj_Pactada']}\\n\\n" if d.get('Adj_Pactada') else ""

    msj = (f"Basada en la planilla de *Arias Hnos.* con vigencia al *{st.session_state.fecha_vigencia}*, aquí tienes el detalle de los costos para el:\\n\\n"
           f"🚘 *Vehículo:* **{d['Modelo']}**\\n\\n"
           f"*Valor del Auto:* ${fmt(d['VM'])}\\n"
           f"*Tipo de Plan:* {tp}\\n"
           f"*Plazo:* 84 Cuotas (Pre-cancelables a Cuota Pura hoy *${fmt(d['CPura'])}*)\\n\\n"
           f"{adj_final}"
           f"*Detalle de Inversión Inicial:*\n"
           f"* *Suscripción:* ${fmt(d['Susc'])}\\n"
           f"* *Cuota Nº 1:* ${fmt(d['C1'])}\\n"
           f"* *Costo Total de Ingreso:* ${fmt(d['Susc']+d['C1'])}.\\n\\n"
           f"-----------------------------------------------------------\\n"
           f"🔥 *BENEFICIO EXCLUSIVO:* Abonando solo **${fmt(d['Adh'])}**, ya cubrís el **INGRESO COMPLETO**. (Ahorro directo de ${fmt(ah)})\\n"
           f"-----------------------------------------------------------\\n\\n"
           f"💳 **DATO CLAVE:** Podés abonar el beneficio con **Tarjeta de Crédito** para patear el pago 30 días. Además, la Cuota Nº 2 recién te llegará a los **60 días**. 🚀\\n\\n"
           f"✨ **EL CAMBIO QUE MERECÉS:** Más allá del ahorro, imaginate lo que va a ser llegar a casa y ver la cara de orgullo de tu familia al ver el **{d['Modelo']}** nuevo. 🥂\\n\\n"
           f"⚠️ **IMPORTANTE:** Solo me quedan **2 cupos disponibles** con estas condiciones. 💼✅\\n\\n"
           f"🎁 Para asegurar la bonificación del **PRIMER SERVICIO** y el **POLARIZADO**, enviame ahora la foto de tu **DNI**. ¿Te parece bien? 📝📲")

    st.write("---")
    html_button = f"""
    <div style="text-align: center;">
        <button onclick="copyToClipboard()" style="background-color: #007bff; color: white; border: none; padding: 20px; border-radius: 12px; font-weight: bold; width: 100%; font-size: 18px; cursor: pointer; box-shadow: 0px 4px 10px rgba(0,0,0,0.2);">📋 COPIAR PARA WHATSAPP</button>
    </div>
    <script>
    function copyToClipboard() {{
        const text = `{msj}`;
        const el = document.createElement('textarea');
        el.value = text;
        document.body.appendChild(el);
        el.select();
        document.execCommand('copy');
        document.body.removeChild(el);
        alert('✅ ¡Copiado!');
    }}
    </script>
    """
    st.components.v1.html(html_button, height=100)
    with st.expander("🔍 Vista Previa"):
        st.text(msj.replace("\\n", "\n"))
else:
    st.info("Cargá la planilla para empezar.")
