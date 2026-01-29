import streamlit as st
import pandas as pd

st.set_page_config(page_title="Arias Hnos. | Ventas", layout="wide")
st.title("🚗 Arias Hnos. | Generador de Presupuestos")

if 'lista_precios' not in st.session_state:
    st.session_state.lista_precios = []

# --- 1. CARGA DE DATOS ---
st.sidebar.header("📥 Carga de Datos")
modo = st.sidebar.radio("Método:", ["Carga Manual", "Subir archivo (.txt)"])

if modo == "Carga Manual":
    with st.sidebar.form("form_carga", clear_on_submit=True):
        modelo = st.selectbox("Modelo", ["TERA", "VIRTUS", "T-CROSS", "NIVUS", "AMAROK", "TAOS"])
        v_movil = st.number_input("Valor Móvil", min_value=0)
        suscrip = st.number_input("Suscripción Lista", min_value=0)
        c1 = st.number_input("Cuota 1 Lista", min_value=0)
        adherido = st.number_input("Beneficio Adherido (Lo que paga)", min_value=0)
        c2_13 = st.number_input("Cuota 2 a 13", min_value=0)
        c_final = st.number_input("Cuota Final", min_value=0)
        c_pura = st.number_input("Cuota Pura", min_value=0)
        if st.form_submit_button("💾 Guardar"):
            nuevo = {"Modelo": modelo, "VM": v_movil, "Susc": suscrip, "C1": c1, "Adh": adherido, "C2_13": c2_13, "CFin": c_final, "CPura": c_pura}
            st.session_state.lista_precios = [a for a in st.session_state.lista_precios if a['Modelo'] != modelo]
            st.session_state.lista_precios.append(nuevo)
            st.rerun()
else:
    archivo = st.sidebar.file_uploader("Subí tu .txt", type=['txt'])
    if archivo:
        try:
            contenido = archivo.getvalue().decode("utf-8")
        except UnicodeDecodeError:
            contenido = archivo.getvalue().decode("latin-1")
        
        lineas = contenido.split("\n")
        temp = []
        for l in lineas:
            p = l.split(",")
            if len(p) >= 8:
                try:
                    temp.append({"Modelo": p[0].strip(), "VM": int(float(p[1])), "Susc": int(float(p[2])), "C1": int(float(p[3])), "Adh": int(float(p[4])), "C2_13": int(float(p[5])), "CFin": int(float(p[6])), "CPura": int(float(p[7]))})
                except ValueError: continue
        if temp:
            st.session_state.lista_precios = temp
            st.sidebar.success("✅ ¡Archivo cargado!")

# --- 2. SELECTOR Y CONSULTA ---
if st.session_state.lista_precios:
    st.divider()
    modelo_sel = st.selectbox("🔍 Seleccioná el vehículo para el cliente:", [a['Modelo'] for a in st.session_state.lista_precios])
    d = next(a for a in st.session_state.lista_precios if a['Modelo'] == modelo_sel)

    # CÁLCULOS
    costo_normal = d['Susc'] + d['C1']
    ahorro = costo_normal - d['Adh']

    # --- 3. FORMATO WHATSAPP CON ADJUDICACIÓN Y EMOJIS ---
    msj = (f"Basada en la planilla de *Arias Hnos.* con vigencia al *05/12/2025*, aquí tienes el detalle para el:\n\n"
           f"🚘 *Vehículo:* {d['Modelo']}\n"
           f"💰 *Valor del Auto:* ${d['VM']:,}\n"
           f"📍 *Tipo de Plan:* Plan 70/30\n"
           f"⌛ *Plazo:* 84 Cuotas (Pre-cancelables a Cuota Pura de *${d['CPura']:,}*)\n\n"
           f"🤝 *ADJUDICACIÓN PACTADA EN CUOTA:* 8, 12 y 24 ✅\n\n"
           f"✳️ *Inversión Inicial:*\n"
           f"👉 *Suscripción:* ${d['Susc']:,}\n"
           f"👉 *Cuota Nº 1:* ${d['C1']:,}\n"
           f"👉 *Costo Normal:* ${costo_normal:,} (Ver Beneficio 👇)\n\n"
           f"-----------------------------------------------------------\n"
           f"🔥 *BENEFICIO EXCLUSIVO:* Abonando solo *${d['Adh']:,}*, ya cubrís el **INGRESO COMPLETO**.\n\n"
           f"💰 *AHORRO DIRECTO HOY: ${ahorro:,}* 🎁\n"
           f"-----------------------------------------------------------\n\n"
           f"✳️ *Cuotas posteriores:*\n"
           f"✅ *Cuotas 2 a 13:* ${d['C2_13']:,}\n"
           f"✅ *Cuotas 14 a 84:* ${d['CFin']:,}\n"
           f"✅ *Cuota Pura:* ${d['CPura']:,}\n\n"
           f"Los cupos con este beneficio son limitados. Si quieres avanzar mándame foto de DNI frente y dorso y reservamos tu unidad. 🎈🎈").replace(",", ".")

    st.subheader("📱 Vista Previa del Mensaje")
    st.info(msj)
    
    link_wa = f"https://wa.me/?text={msj.replace(' ', '%20').replace('\n', '%0A')}"
    st.markdown(f"### [🚀 ENVIAR POR WHATSAPP CON EMOJIS]({link_wa})")
else:
    st.info("👋 Alejandro, primero cargá los datos desde el panel lateral.")
