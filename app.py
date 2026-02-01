import streamlit as st
from datetime import datetime
import os

# Configuración de página
st.set_page_config(page_title="Arias Hnos. | Gestión de Ventas Pro", layout="wide")

# --- FUNCIONES DE APOYO ---
if not os.path.exists("multimedia"):
    os.makedirs("multimedia")

def limpiar_nombre(texto):
    return "".join([c for c in texto if c.isalnum()]).strip()

# --- MEMORIA DE SESIÓN ---
if 'lista_precios' not in st.session_state:
    st.session_state.lista_precios = []
if 'fecha_vigencia' not in st.session_state:
    st.session_state.fecha_vigencia = datetime.now().strftime("%d/%m/%Y")

# PLANTILLA DE CIERRE POR DEFECTO
if 'texto_cierre' not in st.session_state:
    st.session_state.texto_cierre = (
        "💳 *DATO CLAVE:* Podés abonar el beneficio con *Tarjeta de Crédito* para patear el pago 30 días. "
        "Además, la Cuota Nº 2 recién te llegará a los *60 días*. ¡Tenés un mes de gracia para acomodar tus gastos! 🚀\n\n"
        "✨ *EL CAMBIO QUE MERECÉS:* Más allá del ahorro, imaginate lo que va a ser llegar a casa y ver la cara de orgullo "
        "de tu familia al ver el vehículo nuevo. Hoy estamos a un solo paso. 🥂\n\n"
        "⚠️ *IMPORTANTE:* Al momento de enviarte esto, solo me quedan *2 cupos disponibles* con estas condiciones. 💼✅\n\n"
        "🎁 Para asegurar la bonificación del *PRIMER SERVICIO*, enviame ahora la foto de tu **DNI (frente y dorso)**. ¿Te parece bien? 📝📲"
    )

# --- BARRA LATERAL COMPLETA ---
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
                        temp.append({
                            "Modelo": m_final, "VM": int(float(p[1])), "Susc": int(float(p[2])), 
                            "C1": int(float(p[3])), "Adh": int(float(p[4])), "C2_13": int(float(p[5])), 
                            "CFin": int(float(p[6])), "CPura": int(float(p[7])), "Adj_Pactada": "8, 12 y 24"
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
            if st.form_submit_button("✅ Actualizar Precios"):
                for item in st.session_state.lista_precios:
                    if item['Modelo'] == mod_a_editar:
                        item.update({"Modelo": n_n.upper(), "VM": vm, "Susc": su, "C1": c1, "Adh": ad})
                st.rerun()

# --- CUERPO PRINCIPAL ---
if st.session_state.lista_precios:
    st.markdown(f"## 🚗 Arias Hnos. | Vigencia: {st.session_state.fecha_vigencia}")
    
    mod_sel = st.selectbox("🎯 Cliente interesado en:", [a['Modelo'] for a in st.session_state.lista_precios])
    d = next(a for a in st.session_state.lista_precios if a['Modelo'] == mod_sel)
    
    fmt = lambda x: f"{x:,}".replace(",", ".")
    ah = (d['Susc'] + d['C1']) - d['Adh']
    
    # 1. BOTÓN DE COPIADO (ARRIBA)
    msj_copy = (f"Basada en la planilla al *{st.session_state.fecha_vigencia}*\\n\\n"
                f"🚘 *Vehículo:* **{d['Modelo']}**\\n"
                f"*Valor:* ${fmt(d['VM'])}\\n\\n"
                f"🔥 *BENEFICIO EXCLUSIVO:* Abonando solo **${fmt(d['Adh'])}** ya cubrís el ingreso.\\n\\n"
                f"{st.session_state.texto_cierre.replace('\n', '\\n')}")

    st.components.v1.html(f"""
    <div style="text-align: center;"><button onclick="copyToClipboard()" style="background-color: #007bff; color: white; border: none; padding: 20px; border-radius: 12px; font-weight: bold; width: 100%; font-size: 20px; cursor: pointer;">📋 COPIAR TEXTO WHATSAPP</button></div>
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
    """, height=90)

    # 2. VISTA PREVIA (Cerrada por defecto y uniforme)
    with st.expander("👀 VER VISTA PREVIA DEL MENSAJE", expanded=False):
        st.text(f"Vigencia: {st.session_state.fecha_vigencia}\nModelo: {d['Modelo']}\nValor: ${fmt(d['VM'])}\n\nBeneficio: ${fmt(d['Adh'])}\n\n{st.session_state.texto_cierre}")

    # 3. BIBLIOTECA MULTIMEDIA (ABAJO)
    st.write("---")
    f_id = limpiar_nombre(d['Modelo'])
    modelo_folder = os.path.join("multimedia", f_id)
    if not os.path.exists(modelo_folder): os.makedirs(modelo_folder)

    st.subheader(f"📁 Multimedia: {d['Modelo']}")
    
    with st.expander("➕ Cargar / Gestionar Archivos"):
        up = st.file_uploader("Seleccionar archivos", accept_multiple_files=True, key=f"up_{f_id}")
        if up:
            for f in up:
                with open(os.path.join(modelo_folder, f.name), "wb") as f_dest:
                    f_dest.write(f.getbuffer())
            st.rerun()

    files = os.listdir(modelo_folder)
    if files:
        cols = st.columns(3)
        for i, file in enumerate(files):
            f_p = os.path.join(modelo_folder, file)
            ext = file.split(".")[-1].lower()
            with cols[i % 3]:
                with st.container(border=True):
                    if ext in ["jpg", "png", "jpeg"]: st.image(f_p, use_container_width=True)
                    elif ext in ["mp4", "mov"]: st.video(f_p)
                    else: st.info(f"📄 Archivo: {file}")
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        with open(f_p, "rb") as f_file:
                            st.download_button("⬇️ Descargar", f_file, file_name=file, key=f"dl_{f_id}_{i}", use_container_width=True)
                    with c2:
                        if st.button("🗑️ Borrar", key=f"del_{f_id}_{i}", use_container_width=True):
                            os.remove(f_p)
                            st.rerun()
    else:
        st.info("No hay multimedia para este modelo.")
else:
    st.info("👋 Hola, cargá la planilla para empezar.")
