import os
import io
import base64
import numpy as np
from PIL import Image
import streamlit as st
import streamlit.components.v1 as components
from streamlit_drawable_canvas import st_canvas

# ============================================================
# CONFIGURACIÓN GENERAL (SIN SIDEBAR)
# ============================================================
st.set_page_config(
    page_title="Deducción de Sistemas // Krov Industries",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

if "cad_version" not in st.session_state:
    st.session_state.cad_version = 0

# ============================================================
# ESTILOS: BLUEPRINT TÉCNICO CAD Y PANTALLA DIVIDIDA
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&family=JetBrains+Mono:wght@400;600;700&display=swap');

html, body, [data-testid="stAppViewContainer"], .stApp, section.main, .block-container {
    background: transparent !important;
    background-color: transparent !important;
    color: #f1f5f9 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

body {
    background-color: #020617 !important;
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

# Fondo interactivo blueprint animado en Canvas (Cero Lag)
components.html(
    """
    <script>
    (function() {
        const pWin = window.parent;
        const pDoc = pWin.document;
        if (pWin.__CAD_BG_INIT__) return;
        pWin.__CAD_BG_INIT__ = true;

        let canvas = pDoc.getElementById('cad-fluid-canvas');
        if (!canvas) {
            canvas = pDoc.createElement('canvas');
            canvas.id = 'cad-fluid-canvas';
            canvas.style.cssText = 'position:fixed;top:0;left:0;width:100vw;height:100vh;pointer-events:none;z-index:0;background:#020617;';
            pDoc.body.prepend(canvas);
        }

        const ctx = canvas.getContext('2d');
        let w = canvas.width = pWin.innerWidth;
        let h = canvas.height = pWin.innerHeight;

        pWin.addEventListener('resize', () => {
            w = canvas.width = pWin.innerWidth;
            h = canvas.height = pWin.innerHeight;
        });

        const orbs = [
            { x: w * 0.2, y: h * 0.3, r: 270, vx: 0.5, vy: 0.4, color: 'rgba(0, 246, 255, 0.16)' },
            { x: w * 0.75, y: h * 0.4, r: 290, vx: -0.4, vy: 0.5, color: 'rgba(37, 99, 235, 0.15)' },
            { x: w * 0.5, y: h * 0.8, r: 250, vx: 0.4, vy: -0.5, color: 'rgba(255, 170, 0, 0.12)' }
        ];

        function loop() {
            ctx.clearRect(0, 0, w, h);
            ctx.fillStyle = '#020617';
            ctx.fillRect(0, 0, w, h);
            ctx.globalCompositeOperation = 'screen';

            for (let b of orbs) {
                b.x += b.vx;
                b.y += b.vy;
                if (b.x < -100 || b.x > w + 100) b.vx *= -1;
                if (b.y < -100 || b.y > h + 100) b.vy *= -1;

                const g = ctx.createRadialGradient(b.x, b.y, 10, b.x, b.y, b.r);
                g.addColorStop(0, b.color);
                g.addColorStop(1, 'transparent');
                ctx.beginPath();
                ctx.arc(b.x, b.y, b.r, 0, Math.PI * 2);
                ctx.fillStyle = g;
                ctx.fill();
            }
            requestAnimationFrame(loop);
        }
        loop();
    })();
    </script>
    """,
    height=0,
    width=0
)

st.markdown('<div class="brand-signature">Krov Industries · CAD & Física</div>', unsafe_allow_html=True)
st.markdown('<div class="main-title">Deducción de Sistemas</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-lead">Diagramación vectorial técnica y formulación mecanicista de equilibrio</div>', unsafe_allow_html=True)

# CAMPO DE CLAVE OPENAI DIRECTO EN PANTALLA
c_key, c_info = st.columns([1.5, 1])
with c_key:
    api_key_input = st.text_input(
        "Clave de API de OpenAI:",
        type="password",
        value=os.environ.get("OPENAI_API_KEY", ""),
        placeholder="sk-..."
    )
    if api_key_input:
        os.environ["OPENAI_API_KEY"] = api_key_input

col_cad, col_res = st.columns([1.15, 1], gap="large")

with col_cad:
    # Controles organizados en columnas directas (sin contenedores vacíos)
    c1, c2, c3, c4 = st.columns([1.5, 0.9, 0.8, 1.1])
    with c1:
        herramienta = st.selectbox("Herramienta CAD:", ["✏️ Trazo Libre", "📏 Línea Recta", "⏹️ Rectángulo", "⭕ Círculo", "🔺 Polígono"])
    with c2:
        color = st.color_picker("Tinta:", "#00f6ff")
    with c3:
        fill_on = st.checkbox("Relleno", value=False)
    with c4:
        grosor = st.slider("Calibre:", 1, 20, 3)

    mapa = {"Trazo": "freedraw", "Línea": "line", "Rectángulo": "rect", "Círculo": "circle", "Polígono": "polygon"}
    modo_sel = next(v for k, v in mapa.items() if k in herramienta)
    color_relleno = color + "44" if fill_on else "rgba(0,0,0,0)"

    canvas_res = st_canvas(
        fill_color=color_relleno,
        stroke_width=grosor,
        stroke_color=color,
        background_color="#030816",
        height=420,
        width=620,
        drawing_mode=modo_sel,
        key=f"cad_canvas_v{st.session_state.cad_version}",
    )

    st.write("")
    bc1, bc2 = st.columns([3, 1])
    with bc1:
        btn_procesar = st.button("Procesar topología del sistema", type="primary", use_container_width=True)
    with bc2:
        btn_limpiar = st.button("Limpiar plano", type="secondary", use_container_width=True)

    if btn_limpiar:
        st.session_state.cad_version += 1
        if "resultado_cad" in st.session_state:
            del st.session_state.resultado_cad
        st.rerun()

def codificar_canvas(arr_data):
    arr = np.array(arr_data.astype('uint8'))
    img = Image.fromarray(arr).convert('RGB')
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

with col_res:
    st.markdown("#### Formulación Teórica del Sistema")
    if btn_procesar:
        key_val = os.environ.get("OPENAI_API_KEY", "").strip()
        if not key_val:
            st.warning("Introduce tu clave de API de OpenAI en el campo superior para continuar.")
        elif canvas_res.image_data is None or np.std(canvas_res.image_data[:, :, :3]) < 1.0:
            st.warning("El plano CAD carece de trazos suficientes. Dibuja un diagrama antes de procesar.")
        else:
            prog = st.progress(0, text="Iniciando parsing estructural...")
            try:
                from openai import OpenAI
                client = OpenAI(api_key=key_val)
                prog.progress(40, text="Deduciendo leyes de equilibrio...")
                b64 = codificar_canvas(canvas_res.image_data)

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
                st.error(f"Error al analizar el esquema: {e}")

    if "resultado_cad" in st.session_state:
        st.markdown(f'<div class="blueprint-card">{st.session_state.resultado_cad}</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            '<div class="blueprint-card" style="color:#94a3b8; font-style:italic;">'
            'Traza un esquema geométrico en el panel izquierdo y pulsa "Procesar topología" para formular las leyes mecánicas del sistema.'
            '</div>',
            unsafe_allow_html=True
        )
