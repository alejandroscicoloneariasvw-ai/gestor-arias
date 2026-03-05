import streamlit as st
from datetime import datetime
import json

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Arias Hnos. | Gestión de Ventas Pro", layout="wide")

# --- ESTILOS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Segoe+UI:ital,wght@0,400;0,700;1,300&display=swap');
    html, body, [class*="css"], .stTextArea textarea { font-family: 'Segoe UI', sans-serif !important; font-size: 15px !important; }
    .firma-scicolone { font-style: italic; font-weight: 300; font-size: 14px; color: #6c757d; margin-top: -15px; margin-bottom: 20px; }
    .caja-previa { background-color: #ffffff; padding: 25px; border-radius: 12px; border: 1px solid #e0e0e0; }
    </style>
    """, unsafe_allow_html=True)

if 'lista_precios' not in st.session_state:
    st.session_state.lista_precios = []
if 'fecha_vigencia' not in st.session_state:
    st.session_state.fecha_vigencia = datetime.now().strftime("%d/%m/%Y")

if 'texto_cierre' not in st.session_state:
    st.session_state.texto_cierre = (
        "💳 *DATO CLAVE:* Podés abonar el beneficio con *Tarjeta de Crédito* para patear el pago 30 días. "
        "Además, la Cuota Nº 2 recién te llegará a los *60 días*. ¡Tenés un mes de gracia para acomodar tus gastos! 🚀\n\n"
        "✨ *EL CAMBIO QUE MERECÉS:* Imaginate lo que va a ser llegar a casa y ver la cara de orgullo "
        "de tu familia al ver el vehículo nuevo. Hoy estamos a un solo paso. 🥂\n\n"
        "⚠️ *IMPORTANTE:* Al momento de enviarte esto, solo me quedan *2 cupos disponibles* con estas condiciones. 💼✅\n\n"
        "🎁 Para asegurar la bonificación del *PRIMER SERVICIO DE MANTENIMIENTO* y el *POLARIZADO DE REGALO*, enviame ahora la foto de tu "
        "**DNI (frente y dorso)**. Yo reservo el cupo mientras terminás de decidirlo. ¡Arrancá tu nuevo auto! 🚙🏁🏆✅ ¿Te parece bien? 📝📲"
    )

with st.sidebar:
    st.header("📥 Gestión de Datos")
    modo = st.radio("Acción:", ["Usar datos guardados", "Cargar planilla nueva"], horizontal=True) if st.session_state.lista_precios else "Cargar planilla nueva"
    
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
                        temp.append({
                            "Modelo": p[0].strip().upper(), "VM": int(float(p[1])), "Susc": int(float(p[2])), 
                            "C1": int(float(p[3])), "Adh": int(float(p[4])), "C2_13": int(float(p[5])), 
                            "CFin": int(float(p[6])), "CPura": int(float(p[7]))
                        })
                    except: continue
            st.session_state.lista_precios = temp
            st.rerun()
    
    if st.session_state.lista_precios:
        st.write("---")
        st.subheader("📝 Modificar Cierre")
        st.session_state.texto_cierre = st.text_area("Texto de cierre:", value=st.session_state.texto_cierre, height=150)

        st.write("---")
        st.subheader("💰 Editar Variables")
        m_sel_e = st.selectbox("Modelo a editar:", [a['Modelo'] for a in st.session_state.lista_precios])
        d_e = next(a for a in st.session_state.lista_precios if a['Modelo'] == m_sel_e)

        with st.form("f_edit"):
            c_vm = st.number_input("Valor Móvil:", value=int(d_e['VM']))
            c_su = st.number_input("Suscripción:", value=int(d_e['Susc']))
            c_c1 = st.number_input("Cuota 1:", value=int(d_e['C1']))
            c_ad = st.number_input("Beneficio (Adhesión):", value=int(d_e['Adh']))
            c_c2 = st.number_input("Cuota 2 a 13:", value=int(d_e['C2_13']))
            c_cf = st.number_input("Cuota 14 a 84:", value=int(d_e['CFin']))
            c_cp = st.number_input("Cuota Pura:", value=int(d_e['CPura']))
            
            if st.form_submit_button("💾 Guardar Cambios"):
                for item in st.session_state.lista_precios:
                    if item['Modelo'] == m_sel_e:
                        item.update({
