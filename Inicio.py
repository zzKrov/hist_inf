import os
import io
import base64
import numpy as np
from PIL import Image
import streamlit as st
from streamlit_drawable_canvas import st_canvas
from openai import OpenAI

# -----------------------------------------------------------------------------
# CONFIGURACIÓN GENERAL
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Deducción de Sistemas // Krov Industries",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# LÍNEA BASE VISUAL: TOPOLOGÍA VECTORIAL Y GRADIENTES HIPER-ESPACIALES
# -----------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap');

html, body, [data-testid="stAppViewContainer"], .stApp {
    background-color: #05060a !important;
    color: #f1f5f9 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    overflow-x: hidden;
}

[data-testid="stHeader"] { background: transparent !important; }

/* 1. Malla continua de gradientes */
.stApp {
    background: linear-gradient(135deg, #05060a 0%, #150924 30%, #29081e 60%, #060810 100%) !important;
    background-size: 300% 300% !important;
    animation: vectorShift 18s ease infinite alternate !important;
}

@keyframes vectorShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* 2. Fluidos orgánicos */
.fluid-vec-1 {
    position: fixed;
    top: 15%;
    left: -120px;
    width: 520px;
    height: 520px;
    background: radial-gradient(circle, rgba(0, 246, 255, 0.14) 0%, rgba(255, 0, 127, 0.03) 55%, transparent 75%);
    border-radius: 40% 60% 70% 30% / 50% 60% 40% 50%;
    filter: blur(85px);
    animation: vecDrift1 20s infinite alternate ease-in-out;
    pointer-events: none;
    z-index: 0;
}

.fluid-vec-2 {
    position: fixed;
    bottom: 5%;
    right: -100px;
    width: 560px;
    height: 560px;
    background: radial-gradient(circle, rgba(255, 0, 127, 0.12) 0%, rgba(0, 246, 255, 0.03) 55%, transparent 75%);
    border-radius: 60% 40% 50% 50% / 40% 50% 60% 50%;
    filter: blur(90px);
    animation: vecDrift2 24s infinite alternate ease-in-out;
    pointer-events: none;
    z-index: 0;
}

@keyframes vecDrift1 {
    0% { transform: translate(0, 0) scale(1); }
    50% { transform: translate(110px, 60px) scale(1.15); }
    100% { transform: translate(30px, 130px) scale(0.95); }
}

@keyframes vecDrift2 {
    0% { transform: translate(0, 0) scale(1); }
    50% { transform: translate(-100px, -70px) scale(1.2); }
    100% { transform: translate(-20px, -110px) scale(0.9); }
}

.brand-signature {
    text-align: center;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.18em;
    color: #00f6ff;
    text-transform: uppercase;
    margin-bottom: 2px;
}

.main-title {
    font-size: 2.2rem;
    font-weight: 700;
    text-align: center;
    color: #ffffff;
    margin-bottom: 0.2rem;
    text-shadow: 0 0 25px rgba(0, 246, 255, 0.35);
}

.sub-lead {
    text-align: center;
    color: #94a3b8;
    font-size: 0.95rem;
    margin-bottom: 1.8rem;
}

.pipeline-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1.2rem;
    margin: 1.2rem 0 1.8rem 0;
}

.hyper-card {
    background: rgba(10, 13, 22, 0.85);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 10px;
    padding: 18px;
    backdrop-filter: blur(14px);
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.6);
}

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
    border-radius: 12px !important;
    box-shadow: 0 12px 45px rgba(0, 0, 0, 0.9), 0 0 25px rgba(0, 246, 255, 0.2) !important;
}

div.stButton > button {
    border-radius: 6px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.88rem !important;
    background: linear-gradient(135deg, #00f6ff 0%, #ff007f 100%) !important;
    color: #05060a !important;
    font-weight: 700 !important;
    border: none !important;
    padding: 0.8rem 1.6rem !important;
    box-shadow: 0 0 25px rgba(0, 246, 255, 0.35) !important;
    transition: all 0.25s ease !important;
}
</style>

<div class="fluid-vec-1"></div>
<div class="fluid-vec-2"></div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# BARRA LATERAL (HERRAMIENTAS CAD)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### Consola de Trazado CAD")
    api_key_input = st.text_input("OpenAI API Key", type="password", value=os.environ.get("OPENAI_API_KEY", ""))
    if api_key_input:
        os.environ["OPENAI_API_KEY"] = api_key_input

    st.markdown("---")
    tools = {
        "Pincel Libre": "freedraw",
        "Línea Recta": "line",
        "Rectángulo": "rect",
        "Círculo": "circle",
        "Mover / Transformar": "transform"
    }
    sel_tool = st.radio("Herramienta activa:", list(tools.keys()))
    draw_mode = tools[sel_tool]
    stroke_width = st.slider("Grosor de trazo", 1, 30, 4)
    stroke_color = st.color_picker("Color de trazo", "#00f6ff")

st.markdown('<div class="brand-signature">Krov Industries · Física y Geometría</div>', unsafe_allow_html=True)
st.markdown('<div class="main-title">Deducción Topológica de Sistemas</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-lead">Formalización gráfica y extrapolación mecanicista de modelos teóricos</div>', unsafe_allow_html=True)

st.markdown("""
<div class="pipeline-grid">
    <div class="hyper-card">
        <div style="font-family:'JetBrains Mono'; font-size:0.7rem; color:#ffaa00;">ETAPA 01</div>
        <div style="font-size:1.05rem; font-weight:700; color:#fff;">Trazado Vectorial</div>
        <div style="font-size:0.8rem; color:#94a3b8; margin-top:4px;">Inscripción geométrica sobre el plano continuo.</div>
    </div>
    <div class="hyper-card">
        <div style="font-family:'JetBrains Mono'; font-size:0.7rem; color:#00f6ff;">ETAPA 02</div>
        <div style="font-size:1.05rem; font-weight:700; color:#fff;">Parsing Estructural</div>
        <div style="font-size:0.8rem; color:#94a3b8; margin-top:4px;">Extracción de contornos y simetrías elementales.</div>
    </div>
    <div class="hyper-card">
        <div style="font-family:'JetBrains Mono'; font-size:0.7rem; color:#ff007f;">ETAPA 03</div>
        <div style="font-size:1.05rem; font-weight:700; color:#fff;">Formulación Teórica</div>
        <div style="font-size:0.8rem; color:#94a3b8; margin-top:4px;">Deducción de principios de conservación y campos.</div>
    </div>
</div>
""", unsafe_allow_html=True)

_, col_c, _ = st.columns([1, 4.5, 1])

with col_c:
    canvas_result = st_canvas(
        fill_color="rgba(0,0,0,0)",
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        background_color="#060810",
        height=380,
        width=700,
        drawing_mode=draw_mode,
        key="cad_vector_canvas",
    )

    st.write("")
    process_btn = st.button("Procesar topología del sistema", use_container_width=True)

def serialize_canvas(c_data):
    arr = np.array(c_data.astype('uint8'))
    image = Image.fromarray(arr).convert('RGB')
    buf = io.BytesIO()
    image.save(buf, format="JPEG", quality=90)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

if process_btn:
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        st.warning("Introduce una API Key válida de OpenAI en el panel lateral.")
    elif canvas_result.image_data is None or np.std(canvas_result.image_data[:, :, :3]) < 1.0:
        st.warning("El plano carece de trazos suficientes para deducir un sistema.")
    else:
        with col_c:
            with st.spinner("Deduciendo leyes mecánicas del esquema..."):
                try:
                    b64 = serialize_canvas(canvas_result.image_data)
                    client = OpenAI(api_key=api_key)
                    prompt = (
                        "Analiza este diagrama esquemático. Identifica su configuración geométrica y plantea "
                        "una formulación mecanicista formal en español que explique cómo operaría como un sistema de campos, "
                        "vórtices o equilibrio de fuerzas. Estructúralo con claridad técnica."
                    )
                    res = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}]}],
                        max_tokens=600
                    )
                    st.markdown("### Modelo Teórico Deducido:")
                    st.write(res.choices[0].message.content)
                except Exception as e:
                    st.error(f"Fallo durante la evaluación teórica: {e}")
