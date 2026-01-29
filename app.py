import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Arias Hnos. | Ventas", layout="wide")
st.title("🚗 Arias Hnos. | Generador de Presupuestos")

if 'lista_precios' not in st.session_state:
    st.session_state.lista_precios = []
if 'fecha_vigencia' not in st.session_state:
    st.session_state.fecha_vigencia = datetime.now().strftime("%d/%m/%Y")

# --- 1. CARGA DE DATOS ---
st.sidebar.header("📥 Carga de Datos")
modo = st.sidebar.radio("Método:", ["Carga Manual", "Subir archivo (.txt)"])

if modo == "Carga Manual":
    with st.sidebar.form("form_carga", clear_on_submit=True):
        st.session_state.fecha_vigencia = st.text_input("📅 Fecha de Vigencia:", st.session_state.fecha_vigencia)
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
        except:
            contenido = archivo.getvalue().decode("latin-1")
        
        lineas = contenido.split("\n")
        temp = []
        for l in lineas:
            if "/" in l and len(l.strip()) <= 10 and "," not in l:
                st.session_state.fecha_vigencia = l.strip()
                continue
            p = l.split(",")
            if len(p) >= 8:
                try:
                    temp.append({"Modelo": p[0].strip(), "VM": int(float(p[1])), "Susc": int(float(p[2])), "C1": int(float(p[3])), "Adh": int(float(p[4])), "C2_13": int(float(p[5])), "CFin": int(float(p[6])), "CPura": int(float(p[7]))})
                except: continue
        st.session_state.lista_precios = temp

# --- 2. SELECTOR Y CONSULTA ---
if st.session_state.lista_precios:
    st.divider()
    modelo_sel = st.selectbox("🔍 Seleccioná el vehículo:", [a['Modelo'] for a in st.session_state.lista_precios])
    d = next(a for a in st.session_state.lista_precios if a['Modelo'] == modelo_sel)

    costo_normal = d['Susc'] + d['C1']
    ahorro = costo_normal - d['Adh']

    # --- LÓGICA DE ADJUDICACIÓN PACTADA ---
    # Solo para estos tres modelos. Los otros (VIRTUS, AMAROK, TAOS) no muestran nada.
    linea_adjudicacion = ""
    if d['Modelo'] in ["TERA", "NIVUS", "T-CROSS"]:
        linea_adjudicacion = "🎈 *Adjudicación Pactada en Cuota:* 8, 12 y 24\n\n"

    # --- FORMATO WHATSAPP ---
    # Usamos puntos para miles, pero evitamos que el mensaje interprete cuotas como números de teléfono/links
    def fmt(num):
        return f"{num:,}".replace(",", ".")

    msj = (f"Basada en la planilla de *Arias Hnos.* con vigencia al *{st.session_state.fecha_vigencia}*, aquí tienes el detalle de los costos para el:\n\n"
           f"🚘 *Vehículo:* {d['Modelo']}\n\n"
           f"*Valor del Auto:* ${fmt(d['VM'])}\n\n"
           f"*Tipo de Plan:* Plan 70/30\n\n"
           f"*Plazo:* 84 Cuotas (Pre-cancelables a Cuota Pura de *${fmt(d['CPura'])}*)\n\n"
           f"{linea_adjudicacion}\n"
           f"*Detalle de Inversión Inicial:*\n"
           f"* *Suscripción a Financiación:* ${fmt(d['Susc'])}\n"
           f"* *Cuota Nº 1:* ${fmt(d['C1'])}\n"
           f"* *Costo Normal de Ingreso:* ${fmt(costo_normal)}. (Ver Beneficio Exclusivo 👇)\n\n"
           f"-----------------------------------------------------------\n"
           f"🔥 *BENEFICIO EXCLUSIVO:* Abonando solo *${fmt(d['Adh'])}*, ya cubrís el **INGRESO COMPLETO de Cuota 1 y Suscripción**.\n\n"
           f"💰 *AHORRO DIRECTO HOY: ${fmt(ahorro)}*\n"
           f"-----------------------------------------------------------\n\n"
           f"*Esquema de cuotas posteriores:*\n"
           f"* *Cuotas 2 a 13:* ${fmt(d['C2_13'])}\n"
           f"* *Cuotas 14 a 84:* ${fmt(d['CFin'])}\n"
           f"* *Cuota Pura:* ${fmt(d['CPura'])}\n\n"
           f"Los cupos con este beneficio de ingreso son limitados por la vigencia de la planilla. "
           f"Si queda alguna duda a disposición. Si quieres avanzar mándame por este medio foto de DNI de adelante y de atrás "
           f"y te comento como realizaremos este pago Beneficio. 🎈🎈")

    st.subheader("📋 Presupuesto para Copiar")
    st.code(msj, language=None)
    
    st.divider()
    st.write("👇 **Carga Manual (Respaldo):**")
    st.text_area("Seleccioná y copiá de acá:", msj, height=250)

else:
    st.info("👋 Alejandro, cargá los datos para empezar.")
