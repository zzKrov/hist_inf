import os
import io
import base64
import numpy as np
from PIL import Image
import streamlit as st
from streamlit_drawable_canvas import st_canvas

# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================
st.set_page_config(
    page_title="Análisis de Bocetos Técnicos // Krov Industries",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------------------------------------------------
# ESTADO DEL LIENZO PARA RESET COMPLETO
# ------------------------------------------------------------
if "cad_canvas_ver" not in st.session_state:
    st.session_state.cad_canvas_ver = 0

# ============================================================
# ESTILOS VISUALES: NEÓN CIBERNÉTICO LÍQUIDO Y CENTRADO EXACTO
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [data-testid="stAppViewContainer"], .stApp {
    background-color: #05060a !important;
    color: #f1f5f9 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    overflow-x: hidden;
}

[data-testid="stHeader"] { background: transparent !important; }

/* Fondo líquido acelerado por GPU */
.stApp {
    background:
        radial-gradient(circle at 15% 20%, rgba(0, 246, 255, 0.15) 0%, transparent 40%),
        radial-gradient(circle at 85% 30%, rgba(255, 0, 127, 0.15) 0%, transparent 45%),
        linear-gradient(135deg, #05060a 0%, #150920 50%, #05060a 100%) !important;
    background-size: 200% 200% !important;
    animation: vectorLava 14s ease infinite alternate !important;
}

@keyframes vectorLava {
    0% { background-position: 0% 0%; }
    50% { background-position: 100% 100%; }
    100% { background-position: 0% 100%; }
}

.brand-signature {
    text-align: center;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.18em;
    color: #00f6ff;
    text-transform: uppercase;
}

.main-title {
    font-size: 2.2rem;
    font-weight: 700;
    text-align: center;
    color: #ffffff;
    margin-bottom: 0.2rem;
    text-shadow: 0 0 25px rgba(0, 246, 255, 0.4);
}

.sub-lead {
    text-align: center;
    color: #94a3b8;
    font-size: 0.95rem;
    margin-bottom: 1.4rem;
}

.block-container {
    max-width: 760px !important;
    padding-top: 1.8rem !important;
    padding-bottom: 3rem !important;
    margin: 0 auto !important;
}

/* Centrado simétrico del lienzo sin desfasados */
div[data-testid="stCustomComponentV1"] {
    display: flex !important;
    justify-content: center !important;
    width: 100% !important;
}

iframe[title*="canvas"] {
    width: 680px !important;
    height: 380px !important;
    margin: 0 auto !important;
    display: block !important;
    border: 2px solid rgba(0, 246, 255, 0.35) !important;
    border-radius: 10px !important;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.8), 0 0 25px rgba(0, 246, 255, 0.2) !important;
    transition: all 0.25s ease !important;
}

iframe[title*="canvas"]:hover {
    border-color: #00f6ff !important;
    box-shadow: 0 14px 45px rgba(0, 0, 0, 0.9), 0 0 35px rgba(0, 246, 255, 0.4) !important;
}

div.stButton > button[kind="primary"] {
    border-radius: 6px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.88rem !important;
    background: linear-gradient(135deg, #00f6ff 0%, #ff007f 100%) !important;
    color: #05060a !important;
    font-weight: 700 !important;
    border: none !important;
    padding: 0.8rem 1.6rem !important;
    box-shadow: 0 0 20px rgba(0, 246, 255, 0.35) !important;
    transition: all 0.25s ease !important;
}

div.stButton > button[kind="primary"]:hover {
    transform: translateY(-2px) scale(1.02);
    box-shadow: 0 0 35px rgba(0, 246, 255, 0.7) !important;
}

div.stButton > button[kind="secondary"] {
    background: rgba(18, 20, 35, 0.85) !important;
    color: #e4e4e7 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.88rem !important;
    font-weight: 600 !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    border-radius: 6px !important;
    padding: 0.8rem 1.6rem !important;
    transition: all 0.2s ease !important;
}

div.stButton > button[kind="secondary"]:hover {
    transform: translateY(-2px) !important;
    border-color: #ffffff !important;
    color: #ffffff !important;
}

.result-card {
    background: rgba(10, 14, 26, 0.9);
    border-left: 4px solid #00f6ff;
    padding: 20px;
    border-radius: 8px;
    margin-top: 18px;
    line-height: 1.65;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# BARRA LATERAL (HERRAMIENTAS CAD)
# ============================================================
with st.sidebar:
    st.markdown("### Configuración de Trazado")
    api_key = st.text_input("Clave de API de OpenAI:", type="password", value=os.environ.get("OPENAI_API_KEY", ""))
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key

    modo_herramienta = st.radio("Herramienta activa:", ["Pincel Libre", "Línea Recta", "Rectángulo", "Círculo"])
    mapa_herramientas = {"Pincel Libre": "freedraw", "Línea Recta": "line", "Rectángulo": "rect", "Círculo": "circle"}
    draw_mode = mapa_herramientas[modo_herramienta]
    grosor = st.slider("Grosor de trazo:", 1, 25, 4)
    color = st.color_picker("Tinta de trazo:", "#00f6ff")

st.markdown('<div class="brand-signature">Krov Industries · Esquemas</div>', unsafe_allow_html=True)
st.markdown('<div class="main-title">Análisis de Bocetos Técnicos</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-lead">Dibuja un esquema y la IA deducirá el modelo estructural y operativo</div>', unsafe_allow_html=True)

canvas_res = st_canvas(
    fill_color="rgba(0,0,0,0)",
    stroke_width=grosor,
    stroke_color=color,
    background_color="#060810",
    height=380,
    width=680,
    drawing_mode=draw_mode,
    key=f"esquema_canvas_v{st.session_state.cad_canvas_ver}",
)

st.write("")
btn_c1, btn_c2 = st.columns([3, 1])
with btn_c1:
    analizar_btn = st.button("Analizar esquema técnico", type="primary", use_container_width=True)
with btn_c2:
    limpiar_btn = st.button("Limpiar plano", type="secondary", use_container_width=True)

if limpiar_btn:
    st.session_state.cad_canvas_ver += 1
    st.rerun()

if analizar_btn:
    key_val = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key_val:
        st.warning("Introduce tu API Key en la barra lateral para continuar.")
    elif canvas_res.image_data is None or np.std(canvas_res.image_data[:, :, :3]) < 1.0:
        st.warning("El plano está vacío. Traza un diagrama antes de continuar.")
    else:
        with st.spinner("Analizando la configuración del esquema..."):
            try:
                from openai import OpenAI
                client = OpenAI(api_key=key_val)
                arr = np.array(canvas_res.image_data.astype('uint8'))
                img = Image.fromarray(arr).convert('RGB')
                buf = io.BytesIO()
                img.save(buf, format="JPEG", quality=90)
                b64 = base64.b64encode(buf.getvalue()).decode('utf-8')

                prompt = (
                    "Analiza este boceto técnico de forma analítica y directa en español natural. "
                    "Explica qué representa, qué función tienen sus componentes y cómo interactúan entre sí. "
                    "Usa un tono profesional, preciso y sin adornos artificiales."
                )
                resp = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}]}],
                    max_tokens=550
                )
                st.markdown(f'<div class="result-card"><h4>Resultado del análisis:</h4>{resp.choices[0].message.content}</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error al analizar el esquema: {e}")
