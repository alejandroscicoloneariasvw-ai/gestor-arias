import streamlit as st
from datetime import datetime
import pandas as pd

st.set_page_config(page_title="Arias Hnos.", layout="wide")

# --- CSS: EL CUADRITO DE 2x2 CM ---
st.markdown("""
    <style>
    /* Creamos el cuadradito azul de 2x2 cm aprox */
    .stCodeBlock {
        width: 70px !important;
        height: 70px !important;
        overflow: hidden !important;
        border: 3px solid #007bff !important;
        border-radius: 12px !important;
        background-color: #f0f2f6 !important;
    }
    /* Escondemos el texto para que solo quede el icono de copiar */
    .stCodeBlock pre {
        visibility: hidden !important;
    }
    /* Ajustamos el título para que no ocupe tanto espacio */
    h1 {
        font-size: 24px !important;
        padding-top: 0px !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🚗 Arias Hnos. | Ventas")

if 'lista_precios' not in st.session_state:
    st.session_state.lista_precios = []
if 'fecha_vigencia' not in st.session_state:
    st.session_state.fecha_vigencia = datetime.now().strftime("%d/%m/%Y")

# --- 1. CARGA (Sidebar) ---
with st.sidebar:
    st.header("📥 Carga")
    modo = st.radio("Método:", ["Manual", "Archivo (.txt)"])
    if modo == "Manual":
        with st.form("f"):
            st.session_state.fecha_vigencia = st.text_input("Fecha:", st.session_state.fecha_vigencia)
            mod = st.selectbox("Modelo", ["TERA", "VIRTUS", "T-CROSS", "NIVUS", "AMAROK", "TAOS"])
            vm = st.number_input("Valor Móvil", 0)
            su = st.number_input("Suscripción", 0)
            c1 = st.number_input("Cuota 1", 0)
            ad = st.number_input("Paga con Beneficio", 0)
            c2 = st.number_input("Cuota 2-13", 0)
            cf = st.number_input("Cuota Final", 0)
            cp = st.number_input("Cuota Pura", 0)
            if st.form_submit_button("Guardar"):
                nuevo = {"Modelo": mod, "VM": vm, "Susc": su, "C1": c1, "Adh": ad, "C2_13": c2, "CFin": cf, "CPura": cp}
                st.session_state.lista_precios = [a for a in st.session_state.lista_precios if a['Modelo'] != mod]
                st.session_state.lista_precios.append(nuevo)
                st.rerun()
    else:
        arc = st.file_uploader("Subir .txt", type=['txt'])
        if arc:
            cont = arc.getvalue().decode("utf-8", errors="ignore")
            lineas = cont.split("\n")
            temp = []
            for l in lineas:
                if "/" in l and len(l.strip()) <= 10: st.session_state.fecha_vigencia = l.strip(); continue
                p = l.split(",")
                if len(p) >= 8:
                    try: temp.append({"Modelo": p[0].strip(), "VM": int(float(p[1])), "Susc": int(float(p[2])), "C1": int(float(p[3])), "Adh": int(float(p[4])), "C2_13": int(float(p[5])), "CFin": int(float(p[6])), "CPura": int(float(p[7]))})
                    except: continue
            st.session_state.lista_precios = temp

# --- 2. SELECTOR Y MENSAJE ---
if st.session_state.lista_precios:
    mod_sel = st.selectbox("🔍 Vehículo:", [a['Modelo'] for a in st.session_state.lista_precios])
    d = next(a for a in st.session_state.lista_precios if a['Modelo'] == mod_sel)
    
    fmt = lambda x: f"{x:,}".replace(",", ".")
    ah = (d['Susc'] + d['C1']) - d['Adh']
    tp = "Plan 100% financiado" if d['Modelo'] == "VIRTUS" else "Plan 70/30"
    adj = f"🎈 *Adjudicación Pactada en Cuota:* 8, 12 y 24\n\n" if d['Modelo'] in ["TERA", "NIVUS", "T-CROSS"] else ""

    msj = (f"Basada en la planilla de *Arias Hnos.* con vigencia al *{st.session_state.fecha_vigencia}*, aquí tienes el detalle de los costos para el:\n\n"
           f"🚘 *Vehículo:* {d['Modelo']}\n\n*Valor del Auto:* ${fmt(d['VM'])}\n\n*Tipo de Plan:* {tp}\n\n"
           f"*Plazo:* 84 Cuotas (Pre-cancelables a Cuota Pura hoy *${fmt(d['CPura'])}*)\n\n{adj}"
           f"*Detalle de Inversión Inicial:*\n* *Suscripción a Financiación:* ${fmt(d['Susc'])}\n* *Cuota Nº 1:* ${fmt(d['C1'])}\n"
           f"* *Costo Normal de Ingreso:* ${fmt(d['Susc']+d['C1'])}. (Ver Beneficio 👇)\n\n"
           f"-----------------------------------------------------------\n"
           f"🔥 *BENEFICIO EXCLUSIVO:* Abonando solo *${fmt(d['Adh'])}*, ya cubrís el **INGRESO COMPLETO de Cuota 1 y Suscripción**.\n\n"
           f"💰 *AHORRO DIRECTO HOY: ${fmt(ah)}*\n"
           f"-----------------------------------------------------------\n\n"
           f"*Esquema de cuotas posteriores:*\n* *Cuotas 2 a 13:* ${fmt(d['C2_13'])}\n* *Cuotas 14 a 84:* ${fmt(d['CFin'])}\n* *Cuota Pura:* ${fmt(d['CPura'])}\n\n"
           f"⚠️ *IMPORTANTE:* Los cupos con este beneficio por *${fmt(d['Adh'])}* (donde tienes cubierta la suscripción y cuota 1) son limitados por stock de planilla. 💼✅\n\n"
           f"🎁 Además, vas a contar con un **servicio bonificado** y un **polarizado de regalo**.\n\n"
           f"Si queda alguna duda quedo a disposición. Para avanzar con la reserva, envíame por este medio foto de tu **DNI (frente y dorso)** y coordinamos el pago del beneficio. 📝📲")

    # --- DISEÑO MINIMALISTA ---
    col_btn, col_txt = st.columns([1, 4])
    with col_btn:
        st.write("**COPIAR:**")
        st.code(msj, language=None) # Aquí aparece el cuadradito de 2x2 cm
    
    with col_txt:
        st.info("Hacé clic en el icono de las hojitas dentro del cuadro azul.")

    st.divider()
    # Pegado manual bien escondido abajo
    with st.expander("📄 Ver presupuesto / Pegado manual"):
        st.text_area("", msj, height=150)
else:
    st.info("Cargá datos a la izquierda.")
