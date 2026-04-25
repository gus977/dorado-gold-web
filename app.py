import streamlit as st
import requests
from bs4 import BeautifulSoup
from collections import Counter
import random
import time
import matplotlib.pyplot as plt

# Configuración de la página
st.set_page_config(page_title="Dorado Gold - Consola de Predicción", layout="wide")

# Estilo personalizado para emular tu diseño oscuro
st.markdown("""
    <style>
    .main { background-color: #0A0A0A; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #005A9E; color: white; }
    .resultado-box { background-color: #111; border: 1px solid #00D2FF; padding: 20px; border-radius: 10px; text-align: center; }
    .numero-maestro { color: #FF4444; font-size: 24px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES DE LÓGICA (Tus mismas funciones) ---

def fetch_data():
    urls = {
        "Mañana": "https://resultadodelaloteria.com/colombia/dorado-manana",
        "Tarde": "https://resultadodelaloteria.com/colombia/dorado-tarde",
        "Noche": "https://resultadodelaloteria.com/colombia/dorado-noche"
    }
    resultados = {}
    pool_global = []
    
    for k, u in urls.items():
        try:
            r = requests.get(u, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            soup = BeautifulSoup(r.text, 'html.parser')
            nums = [t.text.strip() for t in soup.find_all(['span','td','b']) if t.text.strip().isdigit() and len(t.text.strip())==4]
            if nums:
                resultados[k] = nums
                pool_global.extend(nums)
        except:
            resultados[k] = []
    return resultados, pool_global

def calc_prob(lista):
    if not lista: return "----", ["----", "----"]
    pos = [[] for _ in range(4)]
    for n in lista:
        for i in range(4): pos[i].append(n[i])
    m = "".join([Counter(pos[i]).most_common(1)[0][0] for i in range(4)])
    ex = ["".join([random.choice(list(set(pos[i]))) for i in range(4)]) for _ in range(2)]
    return m, ex

# --- INTERFAZ DE USUARIO ---

st.title("🎰 Dorado Gold - Consola Profesional")

col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    btn_escaneo = st.button("🔄 ESCANEAR WEBS")
with col2:
    if st.button("🔵 VER ÚLTIMOS SORTEOS"):
        st.toast("Cargando últimos resultados...")
with col3:
    if st.button("🗑️ LIMPIAR TODO"):
        st.cache_data.clear()
        st.rerun()

if btn_escaneo:
    with st.spinner('Escaneando y procesando datos...'):
        historial, pool = fetch_data()
        
        # Guardar en estado de sesión para que no se borre al interactuar
        st.session_state['historial'] = historial
        st.session_state['pool'] = pool

if 'historial' in st.session_state:
    historial = st.session_state['historial']
    pool = st.session_state['pool']

    # Panel de Tendencias
    st.subheader("📊 Tendencias por Horario")
    cols_h = st.columns(3)
    
    for idx, horario in enumerate(["Mañana", "Tarde", "Noche"]):
        with cols_h[idx]:
            m, ex = calc_prob(historial.get(horario, []))
            st.markdown(f"""
                <div class="resultado-box">
                    <h3 style="color:#00D2FF">DORADO {horario.upper()}</h3>
                    <p>MAESTRO: <span class="numero-maestro">{m}</span></p>
                    <p style="color:#888">Extras: {ex[0]}, {ex[1]}</p>
                    <p style="color:#FFF; font-size: 0.8em">Último: {historial[horario][0] if historial[horario] else '----'}</p>
                </div>
            """, unsafe_allow_html=True)

    # Gráfica y Ruleta
    st.divider()
    col_g, col_r = st.columns([1, 1])

    with col_g:
        st.subheader("📈 Distribución de Dígitos")
        digits = [int(d) for n in pool for d in n]
        stats = [Counter(digits).get(i, 0) for i in range(10)]
        fig, ax = plt.subplots()
        fig.patch.set_facecolor('#0E1117')
        ax.set_facecolor('#0E1117')
        ax.pie(stats, labels=[str(i) for i in range(10)], autopct='%1.1f%%', textprops={'color':"w"})
        st.pyplot(fig)

    with col_r:
        st.subheader("🎯 Simulador Maestro")
        m_gen, _ = calc_prob(pool)
        st.markdown(f"<h1 style='text-align: center; font-size: 100px; color: #00FF41;'>{m_gen}</h1>", unsafe_allow_html=True)
        if st.button("🎰 GENERAR NUEVA PREDICCIÓN"):
            st.balloons()
