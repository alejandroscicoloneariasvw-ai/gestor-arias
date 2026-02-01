import streamlit as st
from datetime import datetime
import zipfile
import io

# --- CONFIGURACIÓN DE PÁGINA (BLINDADO) ---
st.set_page_config(page_title="Arias Hnos. | Gestión de Ventas Pro", layout="wide")

# --- ESTILOS UNIFICADOS (BLINDADO) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Segoe+UI:ital,wght@0,400;0,700;1,300&display=swap');
    
    html, body, [class*="css"], .stTextArea textarea, .stNumberInput input, .stTextInput input {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
        font-size: 15px !important;
    }
    
    .firma-scicolone {
        font-family: 'Segoe UI', sans-serif;
        font-style: italic;
        font-weight: 300;
        font-size: 14px;
        color: #6c757d;
        margin-top: -15px;
        margin-bottom: 20px;
        letter-spacing: 0.5px;
    }
    
    .caja-previa {
        font-family: 'Segoe UI', sans-serif;
        font-size: 15px;
        line-height: 1.6;
        color: #1a1a1b;
        background-color: #ffffff;
        padding: 25px;
        border-radius: 12px;
        border: 1px solid #e0e0e0;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# --- MEMORIA DE SESIÓN (BLINDADO) ---
if 'lista_precios' not in st.session_state:
    st.session_state.lista_precios = []
if 'fecha_vigencia' not in st.session_state:
    st.session_state.fecha_vigencia = datetime.now().strftime("%d/%m/%Y")
if 'carpetas_media' not in st.session_state:
    st.session_state.carpetas_media = {
        "TERA TRENDLINE MSI": [],
        "NIVUS 200 TSI": [],
        "T-CROSS 200 TSI": [],
        "VIRTUS TRENDLINE 1.6": [],
        "AMAROK 4*2 TRENDLINE 2.0 140 CV": [],
        "TAOS COMFORTLINE 1.4 150 CV": []
    }

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

# --- BARRA LATERAL: GESTIÓN Y EDICIÓN ---
with st.sidebar:
    st.header("📥 Gestión de Datos")
    if st.session_state.lista_precios:
        modo = st.radio("Acción:", ["Usar datos guardados", "Cargar planilla nueva"], horizontal=True)
    else:
        modo = "Cargar planilla nueva"

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
                        m_f = p[0].strip().upper()
                        adj_ini = "8, 12 y 24" if any(x in m_f for x in ["TERA", "NIVUS", "T-CROSS", "VIRTUS"]) else ""
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
        st.subheader("📝 Modificar Cierre")
        st.session_state.texto_cierre = st.text_area("Texto de cierre:", value=st.session_state.texto_cierre, height=500)

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
                        item.update({"Modelo": n_nom.upper(), "VM": n_vm, "Susc": n_su, "C1": n_c1, 
                                     "Adh": n_ad, "C2_13": n_c2, "CFin": n_cf, "CPura": n_cp, "Adj_Pactada": n_adj})
                st.rerun()

# --- CUERPO PRINCIPAL ---
if st.session_state.lista_precios:
    st.markdown("### 🚗 Arias Hnos. | Gestión de Presupuestos")
    st.markdown('<div class="firma-scicolone">by Alejandro Scicolone</div>', unsafe_allow_html=True)
    
    mod_sel = st.selectbox("🎯 Modelo para el cliente:", [a['Modelo'] for a in st.session_state.lista_precios])
    d = next(a for a in st.session_state.lista_precios if a['Modelo'] == mod_sel)
    
    fmt = lambda x: f"{x:,}".replace(",", ".")
    costo_normal = d['Susc'] + d['C1']
    ahorro_total = costo_normal - d['Adh']
    
    if "VIRTUS" in d['Modelo']: tp = "Plan 100% financiado"
    elif any(x in d['Modelo'] for x in ["AMAROK", "TAOS"]): tp = "Plan 60/40"
    elif any(x in d['Modelo'] for x in ["TERA", "NIVUS", "T-CROSS"]): tp = "Plan 70/30"
    else: tp = "Plan estándar"
    
    adj_f = f"🎈 **Adjudicación Pactada en Cuota:** {d['Adj_Pactada']}\\n\\n" if d.get('Adj_Pactada') else ""
    cierre_v = st.session_state.texto_cierre.replace("\n", "\\n")
    
    msj = (f"Basada en la planilla de *Arias Hnos.* con vigencia al **{st.session_state.fecha_vigencia}**, aquí tienes el detalle de los costos para el:\\n\\n"
            f"🚘 **Vehículo:** **{d['Modelo']}**\\n\\n"
            f"**Valor del Auto:** ${fmt(d['VM'])}\\n"
            f"**Tipo de Plan:** {tp}\\n"
            f"**Plazo:** 84 Cuotas\\n\\n"
            f"{adj_f}"
            f"**Detalle de Inversión Inicial:**\\n"
            f"* *Suscripción a Financiación:* ${fmt(d['Susc'])}\\n"
            f"* *Cuota Nº 1:* ${fmt(d['C1'])}\\n"
            f"* **Costo Normal de Ingreso:** ${fmt(costo_normal)} (Ver Beneficio Exclusivo 👇)\\n\\n"
            f"-----------------------------------------------------------\\n"
            f"🔥 **BENEFICIO EXCLUSIVO:** Abonando solo **${fmt(d['Adh'])}**, ya cubrís el **INGRESO COMPLETO de Cuota 1 y Suscripción**.\\n\\n"
            f"💰 **AHORRO DIRECTO HOY: ${fmt(ahorro_total)}**\\n"
            f"-----------------------------------------------------------\\n\\n"
            f"**Esquema de cuotas posteriores:**\\n"
            f"* *Cuotas 2 a 13:* ${fmt(d['C2_13'])}\\n"
            f"* *Cuotas 14 a 84:* ${fmt(d['CFin'])}\\n"
            f"* *Cuota Pura:* ${fmt(d['CPura'])}\\n\\n"
            f"{cierre_v}")

    st.components.v1.html(f"""
    <div style="text-align: center;"><button onclick="copyToClipboard()" style="background-color: #007bff; color: white; border: none; padding: 20px; border-radius: 12px; font-weight: bold; width: 100%; font-size: 18px; cursor: pointer;">📋 COPIAR PARA WHATSAPP</button></div>
    <script>
    function copyToClipboard() {{
        const text = `{msj}`;
        const el = document.createElement('textarea');
        el.value = text.replace(/\\\\n/g, '\\n');
        document.body.appendChild(el);
        el.select();
        document.execCommand('copy');
        document.body.removeChild(el);
        alert('✅ ¡Copiado con éxito!');
    }}
    </script>
    """, height=100)

    with st.expander("👀 Ver Vista Previa del Mensaje"):
        vista_html = msj.replace("\\n", "<br>").replace("**", "<b>").replace("*", "")
        st.markdown(f'<div class="caja-previa">{vista_html}</div>', unsafe_allow_html=True)

    # --- ARCHIVOS MULTIMEDIA ---
    st.write("---")
    st.subheader("📂 Archivos Multimedia")
    
    with st.expander("🆕 Crear Carpeta Nueva"):
        n_c = st.text_input("Nombre del vehículo:").upper()
        if st.button("Confirmar Carpeta"):
            if n_c: 
                st.session_state.carpetas_media[n_c] = []
                st.rerun()

    for carpeta in list(st.session_state.carpetas_media.keys()):
        with st.expander(f"📁 {carpeta}"):
            subida = st.file_uploader(f"Cargar en {carpeta}", accept_multiple_files=True, key=f"up_{carpeta}")
            if subida:
                for arc in subida:
                    if arc.name not in [x['name'] for x in st.session_state.carpetas_media[carpeta]]:
                        st.session_state.carpetas_media[carpeta].append({
                            "name": arc.name, 
                            "data": arc.getvalue(), 
                            "type": arc.type
                        })

            if st.session_state.carpetas_media[carpeta]:
                seleccionados = []
                for i, doc in enumerate(st.session_state.carpetas_media[carpeta]):
                    c_sel, c_img, c_txt, c_del = st.columns([0.5, 1, 4, 1])
                    if c_sel.checkbox("", key=f"chk_{carpeta}_{i}"):
                        seleccionados.append(doc)
                    if "image" in doc['type']: 
                        c_img.image(doc['data'], width=60)
                    else: 
                        c_img.write("📄")
                    c_txt.text(doc['name'])
                    if c_del.button("🗑️", key=f"del_{carpeta}_{i}"):
                        st.session_state.carpetas_media[carpeta].pop(i)
                        st.rerun()
                
                if seleccionados:
                    buf = io.BytesIO()
                    with zipfile.ZipFile(buf, "w") as fzip:
                        for s in seleccionados: 
                            fzip.writestr(s['name'], s['data'])
                    st.download_button(f"📥 Descargar {len(seleccionados)} archivos marcados", buf.getvalue(), f"{carpeta}.zip", "application/zip", use_container_width=True)
else:
    st.info("👋 Hola, carga la lista de precios para empezar.")
