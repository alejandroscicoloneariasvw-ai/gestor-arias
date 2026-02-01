import streamlit as st
from datetime import datetime
import os

# Configuración de página
st.set_page_config(page_title="Arias Hnos. | Gestión Pro", layout="wide")

# --- FUNCIONES DE CARPETA ---
if not os.path.exists("multimedia"):
    os.makedirs("multimedia")

def get_folder_name(modelo):
    return "".join([c for c in modelo if c.isalnum()]).strip()

# --- MEMORIA DE SESIÓN ---
if 'lista_precios' not in st.session_state:
    st.session_state.lista_precios = []
if 'fecha_vigencia' not in st.session_state:
    st.session_state.fecha_vigencia = datetime.now().strftime("%d/%m/%Y")

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("📥 Configuración")
    if st.session_state.lista_precios:
        modo = st.radio("Acción:", ["Usar datos guardados", "Cargar planilla nueva"], horizontal=True)
    else:
        modo = "Cargar planilla nueva"

    if modo == "Cargar planilla nueva":
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
                        temp.append({
                            "Modelo": m_final, "VM": int(float(p[1])), "Susc": int(float(p[2])), 
                            "C1": int(float(p[3])), "Adh": int(float(p[4])), "C2_13": int(float(p[5])), 
                            "CFin": int(float(p[6])), "CPura": int(float(p[7])), "Adj_Pactada": ""
                        })
                    except: continue
            st.session_state.lista_precios = temp
            st.rerun()

    if st.session_state.lista_precios:
        st.write("---")
        st.subheader("📝 Cierre")
        if 'texto_cierre' not in st.session_state:
            st.session_state.texto_cierre = "Cierre estándar de Arias Hnos."
        st.session_state.texto_cierre = st.text_area("Editar cierre:", value=st.session_state.texto_cierre, height=150)

# --- CUERPO PRINCIPAL ---
if st.session_state.lista_precios:
    st.markdown("## 🚗 Arias Hnos. | Gestión de Ventas")
    
    mod_sel = st.selectbox("🎯 Modelo:", [a['Modelo'] for a in st.session_state.lista_precios])
    d = next(a for a in st.session_state.lista_precios if a['Modelo'] == mod_sel)
    
    fmt = lambda x: f"{x:,}".replace(",", ".")
    ah = (d['Susc'] + d['C1']) - d['Adh']
    
    # --- BOTÓN DE COPIADO (PRIORIDAD) ---
    msj_copy = (f"🚘 *Vehículo:* **{d['Modelo']}**\\n"
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
        alert('✅ ¡Copiado!');
    }}
    </script>
    """, height=90)

    # --- BIBLIOTECA MULTIMEDIA (ABAJO Y RÁPIDA) ---
    st.write("---")
    f_name = get_folder_name(d['Modelo'])
    modelo_folder = os.path.join("multimedia", f_name)
    if not os.path.exists(modelo_folder): os.makedirs(modelo_folder)

    st.subheader(f"📁 Multimedia: {d['Modelo']}")
    
    with st.expander("➕ Cargar / Gestionar Archivos"):
        up = st.file_uploader("Subir", accept_multiple_files=True, key=f"up_{f_name}")
        if up:
            for f in up:
                with open(os.path.join(modelo_folder, f.name), "wb") as f_dest:
                    f_dest.write(f.getbuffer())
            st.rerun()

    files = os.listdir(modelo_folder)
    if files:
        cols = st.columns(4)
        for i, file in enumerate(files):
            f_p = os.path.join(modelo_folder, file)
            ext = file.split(".")[-1].lower()
            with cols[i % 4]:
                with st.container(border=True):
                    # Solo mostramos imagen si es foto, para no ralentizar con videos
                    if ext in ["jpg", "png", "jpeg"]:
                        st.image(f_p, use_container_width=True)
                    else:
                        st.write(f"🎥/📄 {file}")
                    
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        with open(f_p, "rb") as f_file:
                            st.download_button("⬇️", f_file, file_name=file, key=f"dl_{f_name}_{i}")
                    with c2:
                        if st.button("🗑️", key=f"del_{f_name}_{i}"):
                            os.remove(f_p)
                            st.cache_data.clear() # Limpia la memoria interna
                            st.rerun()
    else:
        st.info("No hay archivos.")
else:
    st.info("👋 Hola, cargá la planilla para empezar.")
