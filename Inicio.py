import os
import io
import base64
import numpy as np
from PIL import Image
import streamlit as st
from streamlit_drawable_canvas import st_canvas
import openai
from openai import OpenAI

# -----------------------------------------------------------------------------
# CONFIGURACIÓN Y ESTADO DE SESIÓN
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="TESSERACT // Hyperspectral Vector Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Nueva API Key asignada por defecto con resolución jerárquica
DEFAULT_KEY = "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"

def get_current_key():
    if "OPENAI_API_KEY" in st.secrets:
        return st.secrets["OPENAI_API_KEY"]
    return os.getenv("OPENAI_API_KEY", DEFAULT_KEY)

if 'api_key_stored' not in st.session_state:
    st.session_state.api_key_stored = get_current_key()
if 'pipeline_step' not in st.session_state:
    st.session_state.pipeline_step = 1
if 'structural_id' not in st.session_state:
    st.session_state.structural_id = ""
if 'theoretical_model' not in st.session_state:
    st.session_state.theoretical_model = ""
if 'image_buffer' not in st.session_state:
    st.session_state.image_buffer = ""
if 'canvas_epoch' not in st.session_state:
    st.session_state.canvas_epoch = 0

# -----------------------------------------------------------------------------
# MOTOR VISUAL: EFECTOS EXTREMOS, GRADIENTES SOBRESATURADOS Y TRACKING DE MOUSE
# -----------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=JetBrains+Mono:wght@400;700;800&family=Inter:wght@400;600;800&display=swap');

:root {
    --neon-cyan: #00f6ff;
    --neon-magenta: #ff007f;
    --neon-violet: #8a2be2;
    --neon-amber: #ffaa00;
    --neon-lime: #00ff66;
    --bg-void: #05060a;
}

/* Background dinámico con malla de gradiente interactivo */
.stApp {
    background-color: var(--bg-void);
    background-image: 
        radial-gradient(circle at var(--mouse-x, 50%) var(--mouse-y, 50%), rgba(138, 43, 226, 0.28) 0%, rgba(255, 0, 127, 0.12) 28%, rgba(0, 246, 255, 0.08) 55%, transparent 75%),
        radial-gradient(at 15% 15%, rgba(0, 246, 255, 0.18) 0px, transparent 45%),
        radial-gradient(at 85% 85%, rgba(255, 0, 127, 0.22) 0px, transparent 50%),
        linear-gradient(180deg, #05060a 0%, #090b14 100%);
    background-attachment: fixed;
    color: #f1f5f9;
    font-family: 'Inter', sans-serif;
    overflow-x: hidden;
}

/* Títulos y tipografía con gradientes de alto contraste */
.hyper-title {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 800;
    font-size: 2.2rem;
    letter-spacing: -0.03em;
    background: linear-gradient(90deg, #00f6ff 0%, #ff007f 50%, #ffaa00 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    filter: drop-shadow(0 0 25px rgba(0, 246, 255, 0.45));
    margin: 0;
}

.mono-tag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.76rem;
    font-weight: 700;
    letter-spacing: 0.16em;
    color: var(--neon-cyan);
    text-shadow: 0 0 10px rgba(0, 246, 255, 0.6);
}

/* Canvas interactivo de partículas hiper-saturadas */
#hyper-fx-canvas {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    pointer-events: none;
    z-index: 9999;
}

/* Carrusel de etapas con bordes neón vivos */
.pipeline-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1.2rem;
    margin: 1.2rem 0 2rem 0;
}

.hyper-card {
    background: rgba(10, 13, 22, 0.75);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 14px;
    padding: 1.2rem 1.4rem;
    position: relative;
    backdrop-filter: blur(20px);
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6);
    overflow: hidden;
}

.hyper-card::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, transparent, var(--neon-cyan), transparent);
    opacity: 0;
    transition: opacity 0.3s ease;
}

.hyper-card:hover {
    transform: translateY(-5px) scale(1.015);
    border-color: var(--neon-cyan);
    box-shadow: 0 12px 40px rgba(0, 246, 255, 0.35), 0 0 20px rgba(255, 0, 127, 0.25);
}

.hyper-card:hover::after {
    opacity: 1;
}

.hyper-card.active {
    border: 1px solid var(--neon-magenta);
    background: linear-gradient(145deg, rgba(25, 12, 38, 0.85) 0%, rgba(10, 13, 26, 0.95) 100%);
    box-shadow: 0 0 30px rgba(255, 0, 127, 0.4), inset 0 0 15px rgba(0, 246, 255, 0.15);
}

.hyper-card.active::after {
    background: linear-gradient(90deg, var(--neon-cyan), var(--neon-magenta), var(--neon-amber));
    opacity: 1;
}

.hyper-card .card-step {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    font-weight: 800;
    color: var(--neon-amber);
    text-shadow: 0 0 8px rgba(255, 170, 0, 0.5);
    margin-bottom: 0.35rem;
}

.hyper-card .card-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: #ffffff;
    letter-spacing: -0.01em;
}

.hyper-card .card-desc {
    font-size: 0.8rem;
    color: #94a3b8;
    margin-top: 0.35rem;
    line-height: 1.45;
}

/* Lienzo con borde cromático reactivo */
div[data-testid="stCanvas"] {
    border-radius: 18px !important;
    padding: 3px !important;
    background: linear-gradient(135deg, #00f6ff, #ff007f, #8a2be2, #00ff66) !important;
    background-size: 300% 300% !important;
    animation: gradientShift 8s ease infinite !important;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.8), 0 0 35px rgba(0, 246, 255, 0.3) !important;
    margin: 0 auto !important;
}

@keyframes gradientShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

div[data-testid="stCanvas"] canvas {
    border-radius: 15px !important;
    cursor: crosshair !important;
}

/* Botón de acción con pulso de plasma */
div.stButton > button[kind="primary"] {
    background: linear-gradient(90deg, #ff007f 0%, #8a2be2 50%, #00f6ff 100%) !important;
    background-size: 200% auto !important;
    border: none !important;
    color: #ffffff !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: 0.08em !important;
    padding: 0.8rem 2rem !important;
    border-radius: 10px !important;
    box-shadow: 0 0 25px rgba(255, 0, 127, 0.5), 0 0 40px rgba(0, 246, 255, 0.25) !important;
    transition: all 0.3s ease !important;
}

div.stButton > button[kind="primary"]:hover {
    background-position: right center !important;
    transform: scale(1.02) !important;
    box-shadow: 0 0 40px rgba(255, 0, 127, 0.8), 0 0 60px rgba(0, 246, 255, 0.6) !important;
}

/* Bloques de salida */
.terminal-block {
    background: rgba(8, 10, 18, 0.85);
    border: 1px solid rgba(0, 246, 255, 0.2);
    border-left: 4px solid var(--neon-cyan);
    border-radius: 12px;
    padding: 1.4rem;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.6), inset 0 0 20px rgba(0, 246, 255, 0.05);
    backdrop-filter: blur(16px);
}
</style>

<canvas id="hyper-fx-canvas"></canvas>
<script>
// Sistema de estela micrométrica y gradiente interactivo de alto rendimiento
const fxCanvas = document.getElementById('hyper-fx-canvas');
if (fxCanvas) {
    const ctx = fxCanvas.getContext('2d');
    let particles = [];
    const colors = ['#00f6ff', '#ff007f', '#8a2be2', '#ffaa00', '#00ff66'];
    
    function resize() {
        fxCanvas.width = window.innerWidth;
        fxCanvas.height = window.innerHeight;
    }
    resize();
    window.addEventListener('resize', resize);
    
    window.addEventListener('pointermove', (e) => {
        // Actualiza el centro del gradiente en CSS en tiempo real
        const xPercent = (e.clientX / window.innerWidth) * 100;
        const yPercent = (e.clientY / window.innerHeight) * 100;
        document.documentElement.style.setProperty('--mouse-x', `${xPercent}%`);
        document.documentElement.style.setProperty('--mouse-y', `${yPercent}%`);
        
        // Emisión de partículas con blend mode de plasma
        for(let i = 0; i < 3; i++) {
            particles.push({
                x: e.clientX,
                y: e.clientY,
                size: Math.random() * 3.5 + 1.2,
                vx: (Math.random() - 0.5) * 2.2,
                vy: (Math.random() - 0.5) * 2.2,
                color: colors[Math.floor(Math.random() * colors.length)],
                life: 1.0,
                decay: 0.03 + Math.random() * 0.02
            });
        }
        if (particles.length > 80) particles.splice(0, particles.length - 80);
    });
    
    function render() {
        ctx.clearRect(0, 0, fxCanvas.width, fxCanvas.height);
        ctx.globalCompositeOperation = 'lighter';
        
        for (let i = 0; i < particles.length; i++) {
            let p = particles[i];
            ctx.fillStyle = p.color;
            ctx.globalAlpha = p.life;
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
            ctx.fill();
            
            p.x += p.vx;
            p.y += p.vy;
            p.life -= p.decay;
            
            if (p.life <= 0) {
                particles.splice(i, 1);
                i--;
            }
        }
        ctx.globalAlpha = 1.0;
        requestAnimationFrame(render);
    }
    render();
}
</script>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# SIDEBAR: INSTRUMENTACIÓN TÉCNICA (PHOTOSHOP / KRITA / CAD)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("<div class='mono-tag'>// WORKSTATION CONTROL</div>", unsafe_allow_html=True)
    st.markdown("### Consola de Trazado")
    
    with st.expander("Parámetros de Autenticación", expanded=False):
        api_key_input = st.text_input(
            "OpenAI API Key Activa",
            type="password",
            value=st.session_state.api_key_stored,
            help="Clave de servicio cargada automáticamente."
        )
        if api_key_input != st.session_state.api_key_stored:
            st.session_state.api_key_stored = api_key_input

    st.markdown("---")
    st.markdown("<div class='mono-tag'>MODALIDAD GEOMÉTRICA</div>", unsafe_allow_html=True)
    
    tools = {
        "Pincel Libre (Freehand)": "freedraw",
        "Segmento Rectilíneo (Line)": "line",
        "Marco Ortogonal (Rect)": "rect",
        "Proyección Elíptica (Circle)": "circle",
        "Manipulador de Vector (Transform)": "transform"
    }
    selected_tool = st.radio("Herramienta activa", list(tools.keys()), index=0, label_visibility="collapsed")
    draw_mode = tools[selected_tool]
    
    st.markdown("---")
    st.markdown("<div class='mono-tag'>CALIBRE & CROMA</div>", unsafe_allow_html=True)
    stroke_width = st.slider("Calibre del trazo", min_value=1, max_value=35, value=4)
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        stroke_color = st.color_picker("Tinta", "#00f6ff")
    with col_c2:
        fill_active = st.checkbox("Relleno", value=False)
        fill_color_hex = st.color_picker("Pigmento", "#ff007f")
    
    fill_color = fill_color_hex + "44" if fill_active else "rgba(0,0,0,0)"
    bg_canvas = st.color_picker("Plano de fondo", "#060810")

    st.markdown("---")
    if st.button("Limpiar Lienzo (Reset)", use_container_width=True):
        st.session_state.canvas_epoch += 1
        st.session_state.pipeline_step = 1
        st.session_state.structural_id = ""
        st.session_state.theoretical_model = ""
        st.session_state.image_buffer = ""
        st.rerun()

# -----------------------------------------------------------------------------
# CABECERA & CARROUSEL DE FASES
# -----------------------------------------------------------------------------
col_h1, col_h2 = st.columns([0.8, 0.2])
with col_h1:
    st.markdown("<h1 class='hyper-title'>TESSERACT // ANÁLISIS GEOMÉTRICO</h1>", unsafe_allow_html=True)
    st.markdown("<div class='mono-tag'>Deducción mecanicista de sistemas & topología gráfica continua</div>", unsafe_allow_html=True)
with col_h2:
    st.markdown("<div style='text-align:right; font-family:JetBrains Mono; font-weight:800; font-size:1.1rem; color:var(--neon-magenta); text-shadow:0 0 15px rgba(255,0,127,0.7); padding-top:0.8rem;'>REV.2026.09</div>", unsafe_allow_html=True)

# Estado de las 3 fases
step1_status = "active" if st.session_state.pipeline_step == 1 else ""
step2_status = "active" if st.session_state.pipeline_step == 2 else ""
step3_status = "active" if st.session_state.pipeline_step >= 3 else ""

st.markdown(f"""
<div class="pipeline-grid">
    <div class="hyper-card {step1_status}">
        <div class="card-step">FASE 01 // CAPTURA</div>
        <div class="card-title">Diagramación Vectorial</div>
        <div class="card-desc">Inscripción técnica del boceto y formalización de contornos en el plano.</div>
    </div>
    <div class="hyper-card {step2_status}">
        <div class="card-step">FASE 02 // PARSING</div>
        <div class="card-title">Identificación Estructural</div>
        <div class="card-desc">Extracción objetiva de morfología, balance axial y geometría elemental.</div>
    </div>
    <div class="hyper-card {step3_status}">
        <div class="card-step">FASE 03 // EXTRAPOLACIÓN</div>
        <div class="card-title">Formulación de Sistemas</div>
        <div class="card-desc">Deducción de leyes de conservación, límites dinámicos y acoplamiento de campos.</div>
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# LIENZO DE DIBUJO AMPLIADO
# -----------------------------------------------------------------------------
canvas_result = st_canvas(
    fill_color=fill_color,
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color=bg_canvas,
    height=500,
    width=1000,
    drawing_mode=draw_mode,
    key=f"vector_canvas_{st.session_state.canvas_epoch}",
    display_toolbar=True
)

# -----------------------------------------------------------------------------
# MOTOR DE INFERENCIA EN MEMORIA (ALTO RENDIMIENTO)
# -----------------------------------------------------------------------------
col_b1, col_b2, col_b3 = st.columns([1, 2, 1])
with col_b2:
    execute_button = st.button("⚡ PROCESAR TOPOLOGÍA DEL SISTEMA", use_container_width=True, type="primary")

def serialize_canvas_to_base64(canvas_data):
    arr = np.array(canvas_data.astype('uint8'))
    image = Image.fromarray(arr).convert('RGB')
    buf = io.BytesIO()
    image.save(buf, format="JPEG", quality=88)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

if execute_button:
    current_key = st.session_state.api_key_stored.strip()
    if not current_key:
        st.error("API Key requerida. Ingrésala en la consola lateral.")
    elif canvas_result.image_data is not None:
        pixel_array = np.array(canvas_result.image_data)[:, :, :3]
        if np.std(pixel_array) < 1.0:
            st.info("El plano carece de trazos vectoriales. Dibuja un diagrama antes de procesar.")
        else:
            with st.spinner("Decodificando armónicos geométricos y calculando modelo de conservación..."):
                try:
                    b64_image = serialize_canvas_to_base64(canvas_result.image_data)
                    st.session_state.image_buffer = b64_image
                    client = OpenAI(api_key=current_key)

                    # Fase 1: Identificación aséptica y técnica
                    ident_prompt = (
                        "Identifica de forma estrictamente técnica, objetiva y precisa qué representa este dibujo o diagrama. "
                        "Describe los componentes geométricos o la figura en máximo dos oraciones en español formal. "
                        "No agregues interpretaciones poéticas."
                    )

                    id_response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": ident_prompt},
                                    {
                                        "type": "image_url",
                                        "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"}
                                    }
                                ]
                            }
                        ],
                        max_tokens=140,
                        temperature=0.1
                    )
                    
                    id_result = id_response.choices[0].message.content.strip()
                    st.session_state.structural_id = id_result
                    st.session_state.pipeline_step = 2

                    # Fase 2: Formulación científica rigurosa y predictiva
                    theory_prompt = f"""
                    Diagrama registrado: '{id_result}'.

                    Desarrolla una formulación física y mecanicista especulativa en español que interprete este diagrama como el plano de un sistema de frontera o un modelo cosmológico unificado.

                    Criterios obligatorios:
                    - Tono: Monografía académica de investigación avanzada, frío, riguroso, formal y preciso.
                    - Interpreta el dibujo como la solución geométrica a un problema de física fundamental: acoplamiento de campos, dinámica de vórtices, conservación de momento angular o confinamiento de flujo.
                    - Incorpora de forma TOTALMENTE IMPLÍCITA y formal los principios de:
                      1. Arquitectura coherente y orden organizativo fundamental de la materia.
                      2. Polaridad dinámica: dos fuerzas complementarias y opuestas que equilibran la estructura.
                      3. Límites de demarcación geométrica que aseguran la persistencia del sistema en el espacio-tiempo.
                    - PROHIBIDO el lenguaje esotérico, místico o infantil. Debe leerse como un informe técnico de vanguardia.

                    Estructura la respuesta bajo estas tres cabeceras exactas:
                    1. CONFIGURACIÓN DEL SISTEMA Y LÍMITES GEOMÉTRICOS
                    2. MECÁNICA DE ACOPLAMIENTO Y EQUILIBRIO DE FUERZAS
                    3. PROYECCIÓN PREDICTIVA DE COMPORTAMIENTO
                    """

                    theory_response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {
                                "role": "system",
                                "content": "Actúas como investigador en física teórica y dinámica de sistemas no lineales. Tu estilo es técnico, analítico y rigurosamente estructurado."
                            },
                            {"role": "user", "content": theory_prompt}
                        ],
                        max_tokens=650,
                        temperature=0.4
                    )

                    st.session_state.theoretical_model = theory_response.choices[0].message.content
                    st.session_state.pipeline_step = 3

                except openai.AuthenticationError:
                    st.error("Error de autenticación (401): La API Key ingresada no es válida o ha sido revocada por el proveedor. Modifícala en la consola lateral.")
                except Exception as err:
                    st.error(f"Fallo durante la evaluación teórica: {err}")

# -----------------------------------------------------------------------------
# PRESENTACIÓN DE RESULTADOS
# -----------------------------------------------------------------------------
if st.session_state.structural_id:
    st.markdown("---")
    col_out1, col_out2 = st.columns([1, 2.2])

    with col_out1:
        st.markdown("<div class='mono-tag'>// DISCRIMINACIÓN PRIMARIA</div>", unsafe_allow_html=True)
        st.markdown("### Clasificación de Estructura")
        st.markdown(
            f"""
            <div class='terminal-block'>
                <div style='font-family:JetBrains Mono; font-size:0.75rem; color:var(--neon-cyan); margin-bottom:0.4rem;'>VECTOR DE RECONOCIMIENTO:</div>
                <div style='font-size:0.95rem; line-height:1.5;'>{st.session_state.structural_id}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.session_state.image_buffer:
            st.image(
                f"data:image/jpeg;base64,{st.session_state.image_buffer}",
                caption="Plano de proyección procesado",
                use_container_width=True
            )

    with col_out2:
        st.markdown("<div class='mono-tag'>// DERIVACIÓN FORMAL</div>", unsafe_allow_html=True)
        st.markdown("### Formulación del Sistema y Modelo Teórico")
        st.markdown(
            f"""
            <div class='terminal-block' style='border-left-color: var(--neon-magenta);'>
                <div style='white-space: pre-wrap; font-size:0.9rem; line-height:1.65;'>{st.session_state.theoretical_model}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
