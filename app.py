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
        except:
            contenido = archivo.getvalue().decode("latin-1")
        lineas = contenido.split("\n")
        temp = []
        for l in lineas:
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

    # FORMATO EXACTO AL EJEMPLO
    msj = (f"Basada en la planilla de *Arias Hnos.* con vigencia al *05/12/2025*, aquí tienes el detalle de los costos para el:\n\n"
           f"*Vehículo:* {d['Modelo']}\n\n"
           f"*Valor del Auto:* ${d['VM']:,}\n\n"
           f"*Tipo de Plan:* Plan 70/30\n\n"
           f"*Plazo:* 84 Cuotas (Pre-cancelables a Cuota Pura de *${d['CPura']:,}*)\n\n"
           f"*Adjudicación Pactada en Cuota:* 8, 12 y 24\n\n\n"
           f"*Detalle de Inversión Inicial:*\n"
           f"* *Suscripción a Financiación:* ${d['Susc']:,}\n"
           f"* *Cuota Nº 1:* ${d['C1']:,}\n"
           f"* *Costo Normal de Ingreso:* ${costo_normal:,}. (Ver Beneficio Exclusivo 👇)\n\n"
           f"-----------------------------------------------------------\n"
           f"🔥 *BENEFICIO EXCLUSIVO:* Abonando solo *${d['Adh']:,}*, ya cubrís el **INGRESO COMPLETO de Cuota 1 y Suscripción**.\n\n"
           f"💰 *AHORRO DIRECTO HOY: ${ahorro:,}*\n"
           f"-----------------------------------------------------------\n\n"
           f"*Esquema de cuotas posteriores:*\n"
           f"* *Cuotas 2 a 13:* ${d['C2_13']:,}\n"
           f"* *Cuotas 14 a 84:* ${d['CFin']:,}\n"
           f"* *Cuota Pura:* ${d['CPura']:,}\n\n"
           f"Los cupos con este beneficio de ingreso son limitados por la vigencia de la planilla. "
           f"Si queda alguna duda a disposición. Si quieres avanzar mándame por este medio foto de DNI de adelante y de atrás "
           f"y te comento como realizaremos este pago Beneficio. 🎈🎈").replace(",", ".")

    st.subheader("📝 Mensaje Generado")
    
    # --- BOTÓN DE COPIAR ---
    if st.button("📋 COPIAR AUTOMÁTICAMENTE"):
        # Usamos st.code para que sea fácil de copiar con un click en la esquina si el script falla
        st.code(msj, language=None)
        st.success("¡Mensaje listo! Si no se copió solo, hacé clic en el ícono de copiar arriba a la derecha del recuadro gris.")
    
    st.divider()
    
    # --- CUADRO MANUAL (EL QUE PEDISTE DEJAR) ---
    st.write("👇 **Carga Manual (Copiá y pegá de acá si el botón no funciona):**")
    st.text_area("Seleccioná todo este texto:", msj, height=300)

else:
    st.info("👋 Alejandro, cargá los datos a la izquierda para empezar.")
