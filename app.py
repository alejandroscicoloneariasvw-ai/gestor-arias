import streamlit as st
from datetime import datetime
import zipfile
import io

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Arias Hnos. | Gestión de Ventas Pro", layout="wide")

# --- ESTILOS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Segoe+UI:ital,wght@0,400;0,700;1,300&display=swap');
    html, body, [class*="css"] { font-family: 'Segoe UI', sans-serif !important; }
    .firma-scicolone { font-family: 'Segoe UI'; font-style: italic; font-weight: 300; font-size: 14px; color: #6c757d; margin-top: -15px; margin-bottom: 20px; }
    .caja-previa { background-color: #ffffff; padding: 25px; border-radius: 12px; border: 1px solid #e0e0e0; }
    </style>
    """, unsafe_allow_html=True)

# --- MEMORIA DE SESIÓN ---
if 'lista_precios' not in st.session_state: st.session_state.lista_precios = []
if 'fecha_vigencia' not in st.session_state: st.session_state.fecha_vigencia = datetime.now().strftime("%d/%m/%Y")
if 'carpetas_media' not in st.session_state:
    st.session_state.carpetas_media = {
        "TERA TRENDLINE MSI": [], "NIVUS 200 TSI": [], "T-CROSS 200 TSI": [],
        "VIRTUS TRENDLINE 1.6": [], "AMAROK 4*2 TRENDLINE 2.0 140 CV": [], "TAOS COMFORTLINE 1.4 150 CV": []
    }
if 'seleccionados' not in st.session_state: st.session_state.seleccionados = {}

# --- LÓGICA DE BARRA LATERAL (BLINDADA) ---
with st.sidebar:
    st.header("📥 Gestión de Datos")
    if st.session_state.lista_precios:
        modo = st.radio("Acción:", ["Usar datos guardados", "Cargar planilla nueva"], horizontal=True)
    else: modo = "Cargar planilla nueva"

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
                        temp.append({
                            "Modelo": m_f, "VM": int(float(p[1])), "Susc": int(float(p[2])), 
                            "C1": int(float(p[3])), "Adh": int(float(p[4])), "C2_13": int(float(p[5])), 
                            "CFin": int(float(p[6])), "CPura": int(float(p[7])), "Adj_Pactada": ""
                        })
                    except: continue
            st.session_state.lista_precios = temp
            st.rerun()

# --- CUERPO PRINCIPAL ---
if st.session_state.lista_precios:
    st.markdown("### 🚗 Arias Hnos. | Gestión de Presupuestos")
    st.markdown('<div class="firma-scicolone">by Alejandro Scicolone</div>', unsafe_allow_html=True)
    
    mod_sel = st.selectbox("🎯 Modelo para el cliente:", [a['Modelo'] for a in st.session_state.lista_precios])
    d = next(a for a in st.session_state.lista_precios if a['Modelo'] == mod_sel)
    
    # [Lógica de mensaje WhatsApp - se mantiene igual]
    fmt = lambda x: f"{x:,}".replace(",", ".")
    msj = f"Basada en la planilla de Arias Hnos... {d['Modelo']}" # Simplificado para el ejemplo

    with st.expander("👀 Ver Vista Previa del Mensaje"):
        st.markdown(f'<div class="caja-previa">{msj}</div>', unsafe_allow_html=True)

    # --- SECCIÓN MULTIMEDIA MEJORADA ---
    st.write("---")
    st.subheader("📂 Archivos Multimedia")
    
    with st.expander("🆕 Crear Carpeta Nueva"):
        n_c = st.text_input("Nombre:").upper()
        if st.button("Crear"):
            if n_c: st.session_state.carpetas_media[n_c] = []; st.rerun()

    for carpeta in st.session_state.carpetas_media.keys():
        with st.expander(f"📁 {carpeta}"):
            subida = st.file_uploader(f"Cargar en {carpeta}", accept_multiple_files=True, key=f"up_{carpeta}")
            if subida:
                for arc in subida:
                    if arc.name not in [x['name'] for x in st.session_state.carpetas_media[carpeta]]:
                        st.session_state.carpetas_media[carpeta].append({
                            "name": arc.name, "data": arc.getvalue(), "type": arc.type
                        })

            if st.session_state.carpetas_media[carpeta]:
                # Botón de descarga masiva para esta carpeta
                archivos_a_zip = []
                
                st.write("Seleccioná los archivos para descargar en conjunto:")
                for i, doc in enumerate(st.session_state.carpetas_media[carpeta]):
                    col_sel, col_img, col_txt, col_del = st.columns([0.5, 1, 4, 1])
                    
                    # Checkbox de selección
                    sel = col_sel.checkbox("", key=f"sel_{carpeta}_{i}")
                    if sel: archivos_a_zip.append(doc)
                    
                    # Imagen o Icono
                    if "image" in doc['type']: col_img.image(doc['data'], width=50)
                    else: col_img.write("📄")
                    
                    col_txt.text(doc['name'])
                    
                    if col_del.button("🗑️", key=f"del_{carpeta}_{i}"):
                        st.session_state.carpetas_media[carpeta].pop(i)
                        st.rerun()

                # Lógica del ZIP
                if archivos_a_zip:
                    st.write("---")
                    buf = io.BytesIO()
                    with zipfile.ZipFile(buf, "x", zipfile.ZIP_DEFLATED) as f_zip:
                        for a in archivos_a_zip:
                            f_zip.writestr(a['name'], a['data'])
                    
                    st.download_button(
                        label=f"📥 DESCARGAR {len(archivos_a_zip)} ARCHIVOS (ZIP)",
                        data=buf.getvalue(),
                        file_name=f"multimedia_{carpeta.lower().replace(' ','_')}.zip",
                        mime="application/zip",
                        use_container_width=True
                    )
            else:
                st.caption("Carpeta vacía.")

else:
    st.info("👋 Hola, carga la lista de precios para empezar.")
