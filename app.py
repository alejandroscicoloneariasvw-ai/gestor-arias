import streamlit as st
from datetime import datetime
import os

# Configuración de página
st.set_page_config(page_title="Arias Hnos. | Gestión de Ventas Pro", layout="wide")

# --- ASEGURAR CARPETA MULTIMEDIA ---
if not os.path.exists("multimedia"):
    os.makedirs("multimedia")

# --- MEMORIA DE SESIÓN ---
if 'lista_precios' not in st.session_state:
    st.session_state.lista_precios = []
if 'fecha_vigencia' not in st.session_state:
    st.session_state.fecha_vigencia = datetime.now().strftime("%d/%m/%Y")

# PLANTILLA BASE
if 'texto_cierre' not in st.session_state:
    st.session_state.texto_cierre = (
        "💳 *DATO CLAVE:* Podés abonar el beneficio con *Tarjeta de Crédito* para patear el pago 30 días. "
        "Además, la Cuota Nº 2 recién te llegará a los *60 días*. ¡Tenés un mes de gracia para acomodar tus gastos! 🚀\n\n"
        "✨ *EL CAMBIO QUE MERECÉS:* Más allá del ahorro, imaginate lo que va a ser llegar a casa y ver la cara de orgullo "
        "de tu familia al ver el vehículo nuevo. Ese momento de compartirlo con amigos y disfrutar del confort que te ganaste con tu esfuerzo. "
        "Hoy estamos a un solo paso. 🥂\n\n"
        "⚠️ *IMPORTANTE:* Al momento de enviarte esto, solo me quedan *2 cupos disponibles* con estas condiciones de abonar un monto "
        "menor en la Cuota 1 y Suscripción (Ver Beneficio Exclusivo arriba). 💼✅\n\n"
        "🎁 Para asegurar la bonificación del *PRIMER SERVICIO DE MANTENIMIENTO* y el *POLARIZADO DE REGALO*, enviame ahora la foto de tu "
        "**DNI (frente y dorso)**. Yo reservo el cupo mientras terminás de decidirlo, así no perdés el beneficio por falta de stock y "
        "coordinamos el pago del Beneficio Exclusivo. ¿Te parece bien? 📝📲"
    )

# --- BARRA LATERAL: CARGA Y EDICIÓN ---
with st.sidebar:
    st.header("📥 Carga y Edición")
    if st.session_state.lista_precios:
        modo_inicio = st.radio("¿Qué deseas hacer?", ["Usar datos guardados", "Cargar planilla nueva"], horizontal=True)
    else:
        modo_inicio = "Cargar planilla nueva"

    if modo_inicio == "Cargar planilla nueva":
        arc = st.file_uploader("Subir archivo .txt", type=['txt'])
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
            st.rerun()

    if st.session_state.lista_precios:
        st.write("---")
        st.subheader("📝 Editar Cierre")
        st.session_state.texto_cierre = st.text_area("Cierre:", value=st.session_state.texto_cierre, height=200)
        
        st.write("---")
        st.subheader("💰 Editar Precios")
        opciones_actuales = [a['Modelo'] for a in st.session_state.lista_precios]
        mod_a_editar = st.selectbox("Modelo a modificar:", opciones_actuales)
        d_p = next((a for a in st.session_state.lista_precios if a['Modelo'] == mod_a_editar), None)

        with st.form("f_editar"):
            n_n = st.text_input("Nombre:", value=d_p['Modelo'])
            vm = st.number_input("Valor Móvil", value=int(d_p['VM']))
            su = st.number_input("Suscripción", value=int(d_p['Susc']))
            c1 = st.number_input("Cuota 1", value=int(d_p['C1']))
            ad = st.number_input("Beneficio", value=int(d_p['Adh']))
            cp = st.number_input("Cuota Pura", value=int(d_p['CPura']))
            adj_t = st.text_input("Adjudicación:", value=d_p['Adj_Pactada'])
            if st.form_submit_button("✅ Actualizar"):
                nuevo = {"Modelo": n_n.upper(), "VM": vm, "Susc": su, "C1": c1, "Adh": ad, "C2_13": d_p['C2_13'], "CFin": d_p['CFin'], "CPura": cp, "Adj_Pactada": adj_t}
                st.session_state.lista_precios = [a for a in st.session_state.lista_precios if a['Modelo'] != mod_a_editar]
                st.session_state.lista_precios.append(nuevo)
                st.rerun()

# --- CUERPO PRINCIPAL ---
if st.session_state.lista_precios:
    st.markdown("## 🚗 Arias Hnos. | Presupuestos")
    st.markdown(f"<p style='color: gray;'>by Alejandro Scicolone | Vigencia: {st.session_state.fecha_vigencia}</p>", unsafe_allow_html=True)
    
    mod_sel = st.selectbox("🎯 Cliente interesado en:", [a['Modelo'] for a in st.session_state.lista_precios])
    d = next(a for a in st.session_state.lista_precios if a['Modelo'] == mod_sel)
    
    fmt = lambda x: f"{x:,}".replace(",", ".")
    ah = (d['Susc'] + d['C1']) - d['Adh']
    
    if "VIRTUS" in d['Modelo']: tp = "Plan 100% financiado"
    elif "AMAROK" in d['Modelo'] or "TAOS" in d['Modelo']: tp = "Plan 60/40"
    else: tp = "Plan 70/30"
    
    adj_f = f"🎈 *Adjudicación Pactada en Cuota:* {d['Adj_Pactada']}\n\n" if d.get('Adj_Pactada') else ""
    cierre_v = st.session_state.texto_cierre

    # SECCIÓN MULTIMEDIA INDEPENDIENTE
    st.write("---")
    st.subheader(f"📁 Biblioteca Multimedia: {d['Modelo']}")
    
    modelo_folder = os.path.join("multimedia", d['Modelo'].replace(" ", "_"))
    if not os.path.exists(modelo_folder): os.makedirs(modelo_folder)

    # Carga de archivos
    with st.expander("➕ Cargar archivos a este modelo"):
        uploaded_files = st.file_uploader("Arrastrá fotos, videos o PDFs", accept_multiple_files=True)
        if uploaded_files:
            for uf in uploaded_files:
                with open(os.path.join(modelo_folder, uf.name), "wb") as f: f.write(uf.getbuffer())
            st.success("¡Guardado!")
            st.rerun()

    # Visualización de archivos en columnas
    files = os.listdir(modelo_folder)
    if files:
        cols = st.columns(3) # Tres archivos por fila
        for i, file in enumerate(files):
            f_p = os.path.join(modelo_folder, file)
            ext = file.split(".")[-1].lower()
            
            with cols[i % 3]:
                with st.container(border=True):
                    if ext in ["jpg", "png", "jpeg"]:
                        st.image(f_p, use_container_width=True)
                    elif ext in ["mp4", "mov"]:
                        st.video(f_p)
                    else:
                        st.write(f"📕 **{file}**")
                    
                    st.write(f"📄 {file}")
                    c_down, c_del = st.columns([3, 1])
                    with c_down:
                        with open(f_p, "rb") as f:
                            st.download_button("⬇️ Descargar", f, file_name=file, key=f"dl_{file}", use_container_width=True)
                    with c_del:
                        if st.button("🗑️", key=f"del_{file}"):
                            os.remove(f_p)
                            st.rerun()
    else:
        st.info("No hay archivos cargados para este modelo.")

    # SECCIÓN PRESUPUESTO
    st.write("---")
    col_text, col_copy = st.columns([2, 1])
    
    with col_text:
        with st.expander("👀 VER TEXTO DEL PRESUPUESTO", expanded=False):
            texto_limpio = (f"Vigencia: {st.session_state.fecha_vigencia}\n"
                            f"Vehículo: {d['Modelo']}\n"
                            f"Valor: ${fmt(d['VM'])}\n"
                            f"Beneficio: Pagando ${fmt(d['Adh'])} cubrís el ingreso.\n\n"
                            f"{cierre_v}")
            st.text(texto_limpio)

    # BOTÓN DE COPIADO (Independiente)
    msj_copy = (f"Basada en la planilla de *Arias Hnos.* con vigencia al *{st.session_state.fecha_vigencia}*, aquí tienes el detalle de los costos para el:\\n\\n"
                f"🚘 *Vehículo:* **{d['Modelo']}**\\n\\n"
                f"*Valor del Auto:* ${fmt(d['VM'])}\\n"
                f"*Tipo de Plan:* {tp}\\n"
                f"*Plazo:* 84 Cuotas (Pre-cancelables a Cuota Pura hoy *${fmt(d['CPura'])}*)\\n\\n"
                f"{adj_f.replace('\n', '\\n')}"
                f"*Detalle de Inversión Inicial:*\n"
                f"* *Suscripción:* ${fmt(d['Susc'])}\\n"
                f"* *Cuota Nº 1:* ${fmt(d['C1'])}\\n"
                f"* *Costo Total de Ingreso:* ${fmt(d['Susc']+d['C1'])}.\\n\\n"
                f"-----------------------------------------------------------\\n"
                f"🔥 *BENEFICIO EXCLUSIVO:* Abonando solo **${fmt(d['Adh'])}**, ya cubrís el **INGRESO COMPLETO**. (Ahorro directo de ${fmt(ah)})\\n"
                f"-----------------------------------------------------------\\n\\n"
                f"{cierre_v.replace('\n', '\\n')}")

    st.components.v1.html(f"""
    <div style="text-align: center;"><button onclick="copyToClipboard()" style="background-color: #007bff; color: white; border: none; padding: 18px; border-radius: 12px; font-weight: bold; width: 100%; font-size: 18px; cursor: pointer;">📋 COPIAR TEXTO WHATSAPP</button></div>
    <script>
    function copyToClipboard() {{
        const text = `{msj_copy}`;
        const el = document.createElement('textarea');
        el.value = text.replace(/\\\\n/g, '\\n');
        document.body.appendChild(el);
        el.select();
        document.execCommand('copy');
        document.body.removeChild(el);
        alert('✅ ¡Texto Copiado!');
    }}
    </script>
    """, height=100)
else:
    st.info("👋 Hola Alejandro, cargá la planilla para empezar.")
