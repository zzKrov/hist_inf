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
    page_title="Deducción de Sistemas // Krov Industries",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ------------------------------------------------------------
# ESTADO DEL LIENZO PARA RESET COMPLETO
# ------------------------------------------------------------
if "cad_canvas_ver" not in st.session_state:
    st.session_state.cad_canvas_ver = 0

# ============================================================
# ESTILOS VISUALES: BLUEPRINT TÉCNICO CAD Y NEÓN VECTORIAL
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap');

html, body, [data-testid="stAppViewContainer"], .stApp {
    background-color: #030712 !important;
    color: #f1f5f9 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    overflow-x: hidden;
}

[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stSidebar"], section[data-testid="stSidebar"] { display: none !important; }

/* Fondo líquido animado en GPU */
.stApp {
    background:
        radial-gradient(circle at 15% 20%, rgba(0, 246, 255, 0.15) 0%, transparent 40%),
        radial-gradient(circle at 85% 30%, rgba(255, 170, 0, 0.12) 0%, transparent 45%),
        linear-gradient(135deg, #030712 0%, #081a2e 50%, #030712 100%) !important;
    background-size: 200% 200% !important;
    animation: cadLava 15s ease infinite alternate !important;
}

@keyframes cadLava {
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
    max-width: 780px !important;
    padding-top: 1.8rem !important;
    padding-bottom: 3.5rem !important;
    margin: 0 auto !important;
}

/* Centrado simétrico del lienzo sin desfasados */
div[data-testid="stCustomComponentV1"] {
    display: flex !important;
    justify-content: center !important;
    width: 100% !important;
}

iframe[title*="canvas"] {
    width: 700px !important;
    height: 380px !important;
    margin: 0 auto !important;
    display: block !important;
    border: 2px solid rgba(0, 246, 255, 0.35) !important;
    border-radius: 10px !important;
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.8), 0 0 25px rgba(0, 246, 255, 0.2) !important;
    transition: all 0.25s ease !important;
}

iframe[title*="canvas"]:hover {
    border-color: #ffaa00 !important;
    box-shadow: 0 15px 50px rgba(0, 0, 0, 0.9), 0 0 35px rgba(255, 170, 0, 0.4) !important;
}

.cad-toolbar {
    background: rgba(8, 20, 36, 0.9);
    border: 1px solid rgba(0, 246, 255, 0.3);
    border-radius: 8px;
    padding: 10px 16px;
    margin-bottom: 12px;
    backdrop-filter: blur(12px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.6);
}

div.stButton > button[kind="primary"] {
    border-radius: 6px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.88rem !important;
    background: linear-gradient(135deg, #00f6ff 0%, #ffaa00 100%) !important;
    color: #030712 !important;
    font-weight: 700 !important;
    border: none !important;
    padding: 0.8rem 1.6rem !important;
    box-shadow: 0 0 20px rgba(0, 246, 255, 0.35) !important;
    transition: all 0.25s ease !important;
}

div.stButton > button[kind="primary"]:hover {
    transform: translateY(-2px) scale(1.02);
    box-shadow: 0 0 35px rgba(255, 170, 0, 0.7) !important;
}

div.stButton > button[kind="secondary"] {
    background: rgba(10, 20, 35, 0.85) !important;
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

.theory-card {
    background: rgba(8, 18, 32, 0.9);
    border-left: 4px solid #00f6ff;
    padding: 22px;
    border-radius: 8px;
    margin-top: 18px;
    line-height: 1.7;
    box-shadow: 0 10px 30px rgba(0,0,0,0.6);
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="brand-signature">Krov Industries · Modelado Teórico</div>', unsafe_allow_html=True)
st.markdown('<div class="main-title">Deducción de Sistemas</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-lead">Diagramación vectorial técnica y formulación mecanicista de leyes de conservación</div>', unsafe_allow_html=True)

# BARRA DE HERRAMIENTAS CAD TIPO PHOTOSHOP
st.markdown('<div class="cad-toolbar">', unsafe_allow_html=True)
c_t1, c_t2, c_t3, c_t4 = st.columns([1.6, 1, 1, 1])

with c_t1:
    herramienta_cad = st.selectbox(
        "Herramienta CAD:",
        ["✏️ Trazo Libre", "📏 Segmento de Línea", "⏹️ Marco Ortogonal", "⭕ Proyección Elíptica", "🔺 Polígono / Triángulo", "🧹 Borrador"]
    )
with c_t2:
    color_cad = st.color_picker("Tinta:", "#00f6ff")
with c_t3:
    fill_cad = st.checkbox("Relleno", value=False)
with c_t4:
    grosor_cad = st.slider("Calibre:", 1, 30, 4)

st.markdown('</div>', unsafe_allow_html=True)

if "Trazo" in herramienta_cad:
    cad_mode = "freedraw"
    cad_stroke = color_cad
elif "Línea" in herramienta_cad:
    cad_mode = "line"
    cad_stroke = color_cad
elif "Ortogonal" in herramienta_cad:
    cad_mode = "rect"
    cad_stroke = color_cad
elif "Elíptica" in herramienta_cad:
    cad_mode = "circle"
    cad_stroke = color_cad
elif "Polígono" in herramienta_cad:
    cad_mode = "polygon"
    cad_stroke = color_cad
else:
    cad_mode = "freedraw"
    cad_stroke = "#060810"

cad_fill = color_cad + "44" if (fill_cad and "Borrador" not in herramienta_cad) else "rgba(0,0,0,0)"

canvas_result = st_canvas(
    fill_color=cad_fill,
    stroke_width=grosor_cad,
    stroke_color=cad_stroke,
    background_color="#060810",
    height=380,
    width=700,
    drawing_mode=cad_mode,
    key=f"cad_canvas_v{st.session_state.cad_canvas_ver}",
)

st.write("")
btn_c1, btn_c2 = st.columns([3, 1])
with btn_c1:
    process_btn = st.button("Procesar topología del sistema", type="primary", use_container_width=True)
with btn_c2:
    limpiar_cad = st.button("Limpiar plano", type="secondary", use_container_width=True)

if limpiar_cad:
    st.session_state.cad_canvas_ver += 1
    st.rerun()

def serialize_canvas(c_data):
    arr = np.array(c_data.astype('uint8'))
    image = Image.fromarray(arr).convert('RGB')
    buf = io.BytesIO()
    image.save(buf, format="JPEG", quality=90)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

if process_btn:
    key_val = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key_val:
        st.warning("Introduce tu API Key en la variable de entorno OPENAI_API_KEY para continuar.")
    elif canvas_result.image_data is None or np.std(canvas_result.image_data[:, :, :3]) < 1.0:
        st.warning("El plano carece de trazos suficientes. Dibuja un diagrama antes de procesar.")
    else:
        with st.spinner("Decodificando armónicos y calculando leyes de equilibrio mecanicista..."):
            try:
                from openai import OpenAI
                client = OpenAI(api_key=key_val)
                b64 = serialize_canvas(canvas_result.image_data)

                # Prompt estructurado bajo las 3 fases científicas originales
                prompt = (
                    "Actúas como investigador en física teórica y dinámica de sistemas. "
                    "Analiza este diagrama esquemático y formula una deducción física y mecanicista rigurosa en español "
                    "estructurada exactamente bajo estos 3 encabezados:\n\n"
                    "1. CONFIGURACIÓN DEL SISTEMA Y LÍMITES GEOMÉTRICOS\n"
                    "2. MECÁNICA DE ACOPLAMIENTO Y EQUILIBRIO DE FUERZAS\n"
                    "3. PROYECCIÓN PREDICTIVA DE COMPORTAMIENTO\n\n"
                    "Usa un tono formal, claro y estrictamente analítico."
                )
                res = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}]}],
                    max_tokens=650
                )
                st.markdown(f'<div class="theory-card"><h4>Formulación Teórica del Sistema:</h4><br>{res.choices[0].message.content}</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Fallo durante la evaluación teórica: {e}")
