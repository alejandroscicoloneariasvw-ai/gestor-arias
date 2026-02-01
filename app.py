import streamlit as st
from datetime import datetime
import os

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
    
    .stTextArea textarea { background-color: #fdfdfd; }
    
    /* Estilo para simular carpetas */
    .stExpander { border: 1px solid #007bff22 !important; border-radius: 10px !important; margin-bottom: 10px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- MEMORIA DE SESIÓN (INCLUYE MULTIMEDIA) ---
if 'lista_precios' not in st.session_state: st.session_state.lista_precios = []
if 'fecha_vigencia' not in st.session_state: st.session_state.fecha_vigencia = datetime.now().strftime("%d/%m/%Y")
if 'carpetas_media' not in st.session_state:
    st.session_state.carpetas_media = {
        "TERA TRENDLINE MSI": [],
        "NIVUS 200 TSI": [],
        "T-CROSS 200 TSI": [],
        "VIRTUS TRENDLINE 1.6": [],
        "AMAROK 4*2 TRENDLINE 2.0 140 CV": [],
        "TAOS COMFORTLINE 1.4 150 CV": []
    }

# (Se mantiene el texto_cierre y la lógica de sidebar igual que antes)
if 'texto_cierre' not in st.session_state:
    st.session_state.texto_cierre = ("💳 *DATO CLAVE:* Podés abonar el beneficio...") # (Texto completo anterior)

# --- BARRA LATERAL (LÓGICA ANTERIOR MANTENIDA) ---
with st.sidebar:
    st.header("📥 Gestión de Datos")
    # ... (Misma lógica de carga y edición de precios que ya tienes)
    if st.session_state.lista_precios:
        modo = st.radio("Acción:", ["Usar datos guardados", "Cargar planilla nueva"], horizontal=True)
    else: modo = "Cargar planilla nueva"
    # [Aquí va el código del sidebar que ya tienes]

# --- CUERPO PRINCIPAL ---
if st.session_state.lista_precios:
    st.markdown("### 🚗 Arias Hnos. | Gestión de Presupuestos")
    st.markdown('<div class="firma-scicolone">by Alejandro Scicolone</div>', unsafe_allow_html=True)
    
    # [Aquí va la lógica de selección de modelo, mensaje y botón de copiado que ya tienes]
    # ... (Omitido para brevedad pero se mantiene igual en tu archivo)
    
    st.write("---")
    # SECCIÓN NUEVA: ARCHIVOS MULTIMEDIA
    st.subheader("📂 Archivos Multimedia")
    
    # Opción para agregar carpeta nueva
    with st.expander("➕ Agregar Nueva Carpeta de Vehículo"):
        nueva_c = st.text_input("Nombre del nuevo vehículo:")
        if st.button("Crear Carpeta"):
            if nueva_c and nueva_c.upper() not in st.session_state.carpetas_media:
                st.session_state.carpetas_media[nueva_c.upper()] = []
                st.rerun()

    # Visualización de Carpetas
    for carpeta, archivos in st.session_state.carpetas_media.items():
        with st.expander(f"📁 {carpeta}"):
            col_u, col_l = st.columns([1, 2])
            
            with col_u:
                uploaded_files = st.file_uploader(f"Subir a {carpeta}", accept_multiple_files=True, key=f"up_{carpeta}")
                if uploaded_files:
                    for f in uploaded_files:
                        if f.name not in [x['name'] for x in st.session_state.carpetas_media[carpeta]]:
                            st.session_state.carpetas_media[carpeta].append({"name": f.name, "data": f.getvalue()})
            
            with col_l:
                st.write("**Contenido:**")
                for i, file_obj in enumerate(st.session_state.carpetas_media[carpeta]):
                    c1, c2, c3 = st.columns([3, 1, 1])
                    c1.text(f"📄 {file_obj['name']}")
                    c2.download_button("Descargar", file_obj['data'], file_name=file_obj['name'], key=f"dl_{carpeta}_{i}")
                    if c3.button("🗑️", key=f"del_{carpeta}_{i}"):
                        st.session_state.carpetas_media[carpeta].pop(i)
                        st.rerun()

else:
    st.info("👋 Hola, carga la lista de precios para empezar.")
