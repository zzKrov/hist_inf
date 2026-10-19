import os
import io
import base64
import numpy as np
from PIL import Image
import streamlit as st
import streamlit.components.v1 as components
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

if "cad_canvas_ver" not in st.session_state:
    st.session_state.cad_canvas_ver = 0

# ============================================================
# ESTILOS VISUALES: BLUEPRINT TÉCNICO CAD Y PANTALLA DIVIDIDA
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&family=JetBrains+Mono:wght@400;600;700&display=swap');

html, body, [data-testid="stAppViewContainer"], .stApp {
    background-color: #030712 !important;
    color: #f1f5f9 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    overflow-x: hidden;
}

[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stSidebar"], section[data-testid="stSidebar"] { display: none !important; }

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
    max-width: 1250px !important;
    padding-top: 1.6rem !important;
    padding-bottom: 3.5rem !important;
}

iframe[title*="canvas"] {
    width: 620px !important;
    height: 420px !important;
    margin: 0 auto !important;
    display: block !important;
    border: 2px solid rgba(0, 246, 255, 0.4) !important;
    border-radius: 8px !important;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.8), 0 0 20px rgba(0, 246, 255, 0.15) !important;
}

div.stButton > button[kind="primary"] {
    border-radius: 6px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.88rem !important;
    background: linear-gradient(135deg, #00f6ff 0%, #2563eb 100%) !important;
    color: #020617 !important;
    font-weight: 700 !important;
    border: none !important;
    padding: 0.75rem 1.4rem !important;
    box-shadow: 0 0 20px rgba(0, 246, 255, 0.35) !important;
    transition: all 0.25s ease !important;
}

div.stButton > button[kind="primary"]:hover {
    transform: translateY(-2px) scale(1.02);
    box-shadow: 0 0 35px rgba(0, 246, 255, 0.7) !important;
}

div.stButton > button[kind="secondary"] {
    background: rgba(8, 20, 36, 0.85) !important;
    color: #e4e4e7 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.88rem !important;
    font-weight: 600 !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    border-radius: 6px !important;
    padding: 0.75rem 1.4rem !important;
    transition: all 0.2s ease !important;
}

div.stButton > button[kind="secondary"]:hover {
    transform: translateY(-2px) !important;
    border-color: #ffffff !important;
    color: #ffffff !important;
}

.blueprint-card {
    background: rgba(8, 18, 36, 0.92);
    border: 1px solid rgba(0, 246, 255, 0.25);
    border-left: 4px solid #00f6ff;
    padding: 22px;
    border-radius: 8px;
    line-height: 1.7;
    box-shadow: 0 10px 30px rgba(0,0,0,0.6);
}
</style>
""", unsafe_allow_html=True)

# FONDO BLUEPRINT EN GPU
components.html(
    """
    <script>
    (function() {
        const pWin = window.parent;
        const pDoc = pWin.document;

        if (pWin.__CAD_BG_ACTIVE__) return;
        pWin.__CAD_BG_ACTIVE__ = true;

        let canvas = pDoc.getElementById('cad-lava-canvas');
        if (!canvas) {
            canvas = pDoc.createElement('canvas');
            canvas.id = 'cad-lava-canvas';
            canvas.style.cssText = 'position:fixed;top:0;left:0;width:100vw;height:100vh;pointer-events:none;z-index:0;background:#030712;';
            pDoc.body.prepend(canvas);
        }

        const ctx = canvas.getContext('2d');
        let w = canvas.width = pWin.innerWidth;
        let h = canvas.height = pWin.innerHeight;

        pWin.addEventListener('resize', () => {
            w = canvas.width = pWin.innerWidth;
            h = canvas.height = pWin.innerHeight;
        });

        const blobs = [
            { x: w * 0.2, y: h * 0.3, r: 260, vx: 0.5, vy: 0.4, color: 'rgba(0, 246, 255, 0.14)' },
            { x: w * 0.8, y: h * 0.4, r: 290, vx: -0.4, vy: 0.5, color: 'rgba(37, 99, 235, 0.12)' }
        ];

        function animate() {
            ctx.clearRect(0, 0, w, h);
            ctx.fillStyle = '#030712';
            ctx.fillRect(0, 0, w, h);
            ctx.globalCompositeOperation = 'screen';

            for (let b of blobs) {
                b.x += b.vx; b.y += b.vy;
                if (b.x < -100 || b.x > w + 100) b.vx *= -1;
                if (b.y < -100 || b.y > h + 100) b.vy *= -1;

                const grad = ctx.createRadialGradient(b.x, b.y, b.r * 0.05, b.x, b.y, b.r);
                grad.addColorStop(0, b.color);
                grad.addColorStop(1, 'transparent');

                ctx.beginPath();
                ctx.arc(b.x, b.y, b.r, 0, Math.PI * 2);
                ctx.fillStyle = grad;
                ctx.fill();
            }
            ctx.globalCompositeOperation = 'source-over';
            requestAnimationFrame(animate);
        }
        animate();
    })();
    </script>
    """,
    height=0,
    width=0
)

st.markdown('<div class="brand-signature">Krov Industries · CAD & Física</div>', unsafe_allow_html=True)
st.markdown('<div class="main-title">Deducción de Sistemas</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-lead">Diagramación vectorial de esquemas físicos y formulación mecanicista de equilibrio</div>', unsafe_allow_html=True)

col_cad, col_res = st.columns([1.15, 1], gap="large")

with col_cad:
    c_key, c_tool, c_col, c_fill, c_size = st.columns([1.5, 1.2, 0.8, 0.8, 0.9])
    with c_key:
        api_key = st.text_input("OpenAI API Key:", type="password", value=os.environ.get("OPENAI_API_KEY", ""), placeholder="sk-...")
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
    with c_tool:
        herramienta_cad = st.selectbox("Herramienta CAD:", ["✏️ Trazo Libre", "📏 Línea Recta", "⏹️ Rectángulo", "⭕ Círculo", "🔺 Polígono"])
    with c_col:
        color_cad = st.color_picker("Tinta:", "#00f6ff")
    with c_fill:
        fill_cad = st.checkbox("Relleno", value=False)
    with c_size:
        grosor_cad = st.slider("Calibre:", 1, 20, 3)

    mapa = {"Trazo": "freedraw", "Línea": "line", "Rectángulo": "rect", "Círculo": "circle", "Polígono": "polygon"}
    modo_sel = next(v for k, v in mapa.items() if k in herramienta_cad)
    color_relleno = color_cad + "44" if fill_cad else "rgba(0,0,0,0)"

    canvas_res = st_canvas(
        fill_color=color_relleno,
        stroke_width=grosor_cad,
        stroke_color=color_cad,
        background_color="#030816",
        height=420,
        width=620,
        drawing_mode=modo_sel,
        key=f"cad_canvas_v{st.session_state.cad_canvas_ver}",
    )

    st.write("")
    bc1, bc2 = st.columns([3, 1])
    with bc1:
        process_btn = st.button("Procesar topología del sistema", type="primary", use_container_width=True)
    with bc2:
        btn_limpiar = st.button("Limpiar plano", type="secondary", use_container_width=True)

    if btn_limpiar:
        st.session_state.cad_canvas_ver += 1
        if "resultado_cad" in st.session_state:
            del st.session_state.resultado_cad
        st.rerun()

def serialize_canvas(c_data):
    arr = np.array(c_data.astype('uint8'))
    image = Image.fromarray(arr).convert('RGB')
    buf = io.BytesIO()
    image.save(buf, format="JPEG", quality=90)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

with col_res:
    st.markdown("#### Formulación Teórica del Sistema")
    if process_btn:
        key_val = os.environ.get("OPENAI_API_KEY", "").strip()
        if not key_val:
            st.warning("Introduce tu API Key para continuar.")
        elif canvas_res.image_data is None or np.std(canvas_res.image_data[:, :, :3]) < 1.0:
            st.warning("El plano CAD carece de trazos suficientes. Dibuja un diagrama antes de procesar.")
        else:
            prog = st.progress(0, text="Iniciando parsing de vectores...")
            try:
                from openai import OpenAI
                client = OpenAI(api_key=key_val)
                prog.progress(50, text="Deduciendo leyes mecánicas...")
                b64 = serialize_canvas(canvas_res.image_data)

                prompt = (
                    "Actúas como investigador en física teórica y dinámica de sistemas. "
                    "Analiza este diagrama esquemático y formula una deducción física rigurosa y directa en español "
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
                prog.progress(100, text="Deducción completada.")
                st.session_state.resultado_cad = res.choices[0].message.content
            except Exception as e:
                st.error(f"Fallo durante la evaluación teórica: {e}")

    if "resultado_cad" in st.session_state:
        st.markdown(f'<div class="blueprint-card">{st.session_state.resultado_cad}</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            '<div class="blueprint-card" style="color:#94a3b8; font-style:italic;">'
            'Traza un esquema geométrico en el panel izquierdo y pulsa "Procesar topología" para formular las leyes mecánicas del sistema.'
            '</div>',
            unsafe_allow_html=True
        )
