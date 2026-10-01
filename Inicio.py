import os
import io
import base64
import numpy as np
from PIL import Image
import streamlit as st
from streamlit_drawable_canvas import st_canvas
from openai import OpenAI

# -----------------------------------------------------------------------------
# CONFIGURACIÓN GENERAL Y ESTADO DE SESIÓN
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Tesseract // Decodificador Morfogenético",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded"
)

DEFAULT_API_KEY = os.getenv(
    "OPENAI_API_KEY",
    "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"
)

if 'step' not in st.session_state:
    st.session_state.step = 1  # 1: Trazo, 2: Decodificación, 3: Exégesis
if 'morph_analysis' not in st.session_state:
    st.session_state.morph_analysis = ""
if 'prophecy_thesis' not in st.session_state:
    st.session_state.prophecy_thesis = ""
if 'encoded_image' not in st.session_state:
    st.session_state.encoded_image = ""
if 'canvas_counter' not in st.session_state:
    st.session_state.canvas_counter = 0

# -----------------------------------------------------------------------------
# ESTILOS VISUALES: MINIMALISMO OCULTO, GRADIENTES, PARTICULAS Y TOOLBAR
# -----------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@500;700&family=JetBrains+Mono:wght@300;400;600&family=Inter:wght@300;400;600&display=swap');

:root {
    --bg-primary: #090a0f;
    --card-bg: rgba(16, 19, 28, 0.78);
    --border-color: rgba(212, 175, 55, 0.22);
    --gold: #d4af37;
    --gold-glow: rgba(212, 175, 55, 0.4);
    --accent-cyan: #5ce1e6;
    --text-dim: #9aa4b2;
}

/* Base theme */
.stApp {
    background: radial-gradient(circle at 50% 0%, #151928 0%, #08090d 75%);
    color: #e6ebf2;
    font-family: 'Inter', sans-serif;
}

/* Header typography */
h1, h2, h3, .esoteric-title {
    font-family: 'Cinzel', serif !important;
    letter-spacing: 0.08em;
}

.sub-tech {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82rem;
    color: var(--accent-cyan);
    letter-spacing: 0.12em;
    text-transform: uppercase;
}

/* Mouse trail spark effect overlay */
#trail-canvas {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    pointer-events: none;
    z-index: 9999;
}

/* Pipeline Status Carousel Cards */
.pipeline-container {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 1.2rem;
    margin: 1rem 0 2rem 0;
}

.step-card {
    background: var(--card-bg);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 1.1rem 1.3rem;
    position: relative;
    backdrop-filter: blur(12px);
    transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.35);
    overflow: hidden;
}

.step-card::before {
    content: "";
    position: absolute;
    inset: 0;
    background: radial-gradient(circle at top right, rgba(212, 175, 55, 0.12), transparent 70%);
    opacity: 0;
    transition: opacity 0.35s ease;
}

.step-card:hover {
    transform: translateY(-4px);
    border-color: var(--gold);
    box-shadow: 0 10px 30px var(--gold-glow);
}

.step-card:hover::before {
    opacity: 1;
}

.step-card.active {
    border: 1px solid var(--gold);
    background: linear-gradient(145deg, rgba(25, 30, 46, 0.9), rgba(13, 16, 24, 0.9));
    box-shadow: 0 0 22px rgba(212, 175, 55, 0.25);
}

.step-number {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: var(--gold);
    margin-bottom: 0.3rem;
}

.step-title {
    font-weight: 600;
    font-size: 0.98rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.step-desc {
    font-size: 0.78rem;
    color: var(--text-dim);
    margin-top: 0.3rem;
}

/* Canvas Wrapper Style */
div[data-testid="stCanvas"] {
    border-radius: 16px !important;
    border: 1px solid rgba(212, 175, 55, 0.3) !important;
    box-shadow: 0 15px 45px rgba(0, 0, 0, 0.6), 0 0 15px rgba(92, 225, 230, 0.08) !important;
    overflow: hidden !important;
    margin: 0 auto;
}

div[data-testid="stCanvas"] canvas {
    cursor: crosshair !important;
}

/* Exegesis result cards */
.terminal-block {
    background: rgba(11, 14, 21, 0.85);
    border: 1px solid rgba(212, 175, 55, 0.25);
    border-left: 3px solid var(--gold);
    border-radius: 10px;
    padding: 1.4rem;
    font-size: 0.92rem;
    line-height: 1.65;
    position: relative;
    backdrop-filter: blur(10px);
}
</style>

<canvas id="trail-canvas"></canvas>
<script>
// Spark & Constellation particle trail
const trailCanvas = document.getElementById('trail-canvas');
if (trailCanvas) {
    const ctx = trailCanvas.getContext('2d');
    let particles = [];
    
    function resize() {
        trailCanvas.width = window.innerWidth;
        trailCanvas.height = window.innerHeight;
    }
    resize();
    window.addEventListener('resize', resize);
    
    window.addEventListener('mousemove', (e) => {
        for(let i=0; i<2; i++) {
            particles.push({
                x: e.clientX,
                y: e.clientY,
                size: Math.random() * 2.2 + 0.8,
                speedX: (Math.random() - 0.5) * 1.5,
                speedY: (Math.random() - 0.5) * 1.5,
                opacity: 1,
                decay: 0.03 + Math.random() * 0.02,
                color: Math.random() > 0.5 ? '212, 175, 55' : '92, 225, 230'
            });
        }
    });

    function animate() {
        ctx.clearRect(0, 0, trailCanvas.width, trailCanvas.height);
        for (let i = 0; i < particles.length; i++) {
            let p = particles[i];
            ctx.fillStyle = `rgba(${p.color}, ${p.opacity})`;
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
            ctx.fill();
            p.x += p.speedX;
            p.y += p.speedY;
            p.opacity -= p.decay;
            if (p.opacity <= 0) {
                particles.splice(i, 1);
                i--;
            }
        }
        requestAnimationFrame(animate);
    }
    animate();
}
</script>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# SIDEBAR: PALETA DE HERRAMIENTAS TIPO STUDIO (PHOTOSHOP / KRITA)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("<div class='sub-tech'>// ARCHETYPE ATELIER</div>", unsafe_allow_html=True)
    st.markdown("### ⚚ Consola de Instrumentación")
    
    with st.expander("🔑 Credencial de Acceso", expanded=False):
        api_key = st.text_input(
            "Vector Token / API Key",
            type="password",
            value=DEFAULT_API_KEY,
            help="Clave OpenAI preconfigurada de forma predeterminada."
        )
    
    st.markdown("---")
    st.markdown("**📐 Modalidad del Vector**")
    
    draw_mode_map = {
        "Pincel Libre (Freehand)": "freedraw",
        "Trazo Rectilíneo (Line)": "line",
        "Polígono Cuadrangular (Rect)": "rect",
        "Círculo / Órbita (Circle)": "circle",
        "Transformar Elemento": "transform"
    }
    tool_select = st.radio(
        "Herramienta Activa",
        options=list(draw_mode_map.keys()),
        index=0,
        label_visibility="collapsed"
    )
    drawing_mode = draw_mode_map[tool_select]
    
    st.markdown("---")
    st.markdown("**🎨 Cromática y Saturación**")
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        stroke_color = st.color_picker("Tinta", "#d4af37")
    with col_c2:
        fill_toggle = st.toggle("Activar Relleno", value=False)
        fill_color_raw = st.color_picker("Relleno", "#1c2233")
    
    fill_color = fill_color_raw + "55" if fill_toggle else "rgba(0,0,0,0)"

    st.markdown("---")
    st.markdown("**⚙️ Calibre y Geometría**")
    stroke_width = st.slider("Calibre del Puntero (Grosor)", min_value=1, max_value=35, value=4)
    canvas_bg = st.color_picker("Plano de Fondo", "#0c0e14")
    
    st.markdown("---")
    if st.button("🧹 Purificar Lienzo (Reset)", use_container_width=True):
        st.session_state.canvas_counter += 1
        st.session_state.step = 1
        st.session_state.morph_analysis = ""
        st.session_state.prophecy_thesis = ""
        st.session_state.encoded_image = ""
        st.rerun()

# -----------------------------------------------------------------------------
# CABECERA Y PIPELINE STATUS CAROUSEL (3 PASOS)
# -----------------------------------------------------------------------------
col_head1, col_head2 = st.columns([0.75, 0.25])
with col_head1:
    st.markdown("<h1 style='margin-bottom:0.1rem;'>TESSERACT // MOTOR DE SÍNTESIS</h1>", unsafe_allow_html=True)
    st.markdown("<div class='sub-tech'>Inscripción Morfogenética y Decodificación Teórica Unificada</div>", unsafe_allow_html=True)
with col_head2:
    st.markdown("<div style='text-align:right; font-size:1.6rem; color: #d4af37; padding-top:0.6rem;'>🜁 ⬡ 🜂 ☿ ☉</div>", unsafe_allow_html=True)

# Indicador dinámico de etapas
s1_active = "active" if st.session_state.step == 1 else ""
s2_active = "active" if st.session_state.step == 2 else ""
s3_active = "active" if st.session_state.step >= 3 else ""

st.markdown(f"""
<div class="pipeline-container">
    <div class="step-card {s1_active}">
        <div class="step-number">PHASE 01 // GEOMETRÍA PRIMA</div>
        <div class="step-title"><span>✍️</span> Génesis del Trazo</div>
        <div class="step-desc">Proyección de la forma en el reticulado euclidiano mediante trazo guiado.</div>
    </div>
    <div class="step-card {s2_active}">
        <div class="step-number">PHASE 02 // OBSERVACIÓN COGNITIVA</div>
        <div class="step-title"><span>👁️</span> Análisis Morfológico</div>
        <div class="step-desc">Aislamiento de simetrías, arquetipos visuales y vectores topológicos.</div>
    </div>
    <div class="step-card {s3_active}">
        <div class="step-number">PHASE 03 // EXÉGESIS COSMOLÓGICA</div>
        <div class="step-title"><span>📐</span> Síntesis Profética</div>
        <div class="step-desc">Deducción teórico-científica del boceto como plano cosmogónico implícito.</div>
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# LIENZO PRINCIPAL (EXPANSIVO Y FLUIDO)
# -----------------------------------------------------------------------------
st.markdown("<div style='text-align:center; font-size:0.8rem; color:#8c96a8; margin-bottom: 0.4rem;'>MATRIZ DE DIBUJO ACTIVA // ALINEA LOS VECTORES EN EL PLANO</div>", unsafe_allow_html=True)

canvas_result = st_canvas(
    fill_color=fill_color,
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color=canvas_bg,
    height=480,
    width=980,
    drawing_mode=drawing_mode,
    key=f"vector_canvas_{st.session_state.canvas_counter}",
    display_toolbar=True
)

# -----------------------------------------------------------------------------
# INFERENCIA Y PROCESAMIENTO CON OPTIMIZACIÓN EN MEMORIA
# -----------------------------------------------------------------------------
col_act1, col_act2, col_act3 = st.columns([1, 2, 1])
with col_act2:
    analyze_trigger = st.button("🔮 DECODIFICAR FORMA & CONSTRUIR TEORÍA", use_container_width=True, type="primary")

def process_canvas_image_to_base64(canvas_data):
    """Convierte la matriz de píxeles directamente en memoria a base64 sin I/O en disco"""
    img_array = np.array(canvas_data.astype('uint8'))
    pil_img = Image.fromarray(img_array).convert('RGB')
    buffer = io.BytesIO()
    pil_img.save(buffer, format="JPEG", quality=85)
    return base64.b64encode(buffer.getvalue()).decode('utf-8')

if analyze_trigger:
    if canvas_result.image_data is not None:
        # Validar si el lienzo no está vacío (variación mínima en canales)
        raw_arr = np.array(canvas_result.image_data)[:, :, :3]
        if np.std(raw_arr) < 1.0:
            st.warning("El plano receptor está desprovisto de trazos. Inscribe una figura antes de proceder.")
        else:
            with st.spinner("Decodificando topología del trazo y calculando armónicos cuánticos..."):
                try:
                    b64_img = process_canvas_image_to_base64(canvas_result.image_data)
                    st.session_state.encoded_image = b64_img
                    client = OpenAI(api_key=api_key)

                    # Fase 1: Identificación morfológica precisa
                    prompt_identification = (
                        "Eres un sistema óptico avanzado de análisis topológico. Describe objetivamente, "
                        "en español y en no más de 3 oraciones concisas, exactamente qué figura, forma, diagrama "
                        "o boceto ha sido dibujado en la imagen."
                    )

                    response_ident = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": prompt_identification},
                                    {
                                        "type": "image_url",
                                        "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}
                                    }
                                ]
                            }
                        ],
                        max_tokens=220,
                        temperature=0.2
                    )

                    morph_text = response_ident.choices[0].message.content.strip()
                    st.session_state.morph_analysis = morph_text
                    st.session_state.step = 2

                    # Fase 2: Formulación Teórica Profética con Simbolismo Cosmogónico Implícito
                    # Se mantiene una retórica rigurosa, secular y físico-matemática,
                    # integrando de fondo las leyes herméticas, geometría sagrada y dualidad constructiva.
                    prompt_synthesis = f"""
                    A partir de este boceto identificado: '{morph_text}'.
                    Formula una hipótesis científica especulativa, hiper-avanzada y de tono profético en español.
                    
                    Lineamientos de estilo:
                    - Plantea el boceto no como un dibujo ordinario, sino como el plano esquemático o la huella matemática de una tecnología de frontera, una singularidad topológica o una ley cosmológica no resuelta (ej. fluctuaciones del vacío, calibración dimensional, acoplamiento simétrico, transmutación de la materia informacional).
                    - Estructura el texto con lenguaje riguroso y futurista: usa términos de física teórica, geometría proyectiva y termodinámica cuántica.
                    - Incorpora de forma COMPLETAMENTE IMPLÍCITA y velada la visión cosmogónica de la dualidad armónica (fuerzas gemelas o pilares polares), el principio del Gran Arquitecto o mente unificadora del cosmos, el compás/escuadra como límites de la materia y el espíritu, y el orden que emerge del caos primordial.
                    - NUNCA menciones palabras explícitas como 'masonería', 'esoterismo', 'oculto', 'mágico', 'alquimia' o 'hechizo'. Mantén un tono sobrio, elegante, oracular y estrictamente académico-científico.
                    - Divide la respuesta en 3 secciones marcadas:
                      1. [DIAGNÓSTICO TOPOLÓGICO]: Significado del vector geométrico.
                      2. [HIPÓTESIS DE SINGULARIDAD]: Su manifestación como ley o dispositivo cósmico.
                      3. [PROGNOSIS DEL ORDEN CONSTRUCTIVO]: Lo que su realización predice para la evolución del universo observable.
                    """

                    response_prophecy = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "Eres el Oráculo Teórico de ARCHETYPE: una inteligencia que traduce geometrías elementales en teoremas de física unificada y cosmogénesis profética."},
                            {"role": "user", "content": prompt_synthesis}
                        ],
                        max_tokens=650,
                        temperature=0.75
                    )

                    st.session_state.prophecy_thesis = response_prophecy.choices[0].message.content
                    st.session_state.step = 3

                except Exception as e:
                    st.error(f"Falla en la matriz de inferencia: {e}")

# -----------------------------------------------------------------------------
# VISUALIZACIÓN DE RESULTADOS
# -----------------------------------------------------------------------------
if st.session_state.morph_analysis:
    st.markdown("---")
    res_col1, res_col2 = st.columns([1, 2.2])

    with res_col1:
        st.markdown("<div class='sub-tech'>// OBSERVACIÓN ÓPTICA</div>", unsafe_allow_html=True)
        st.markdown("### Morfología Registrada")
        st.markdown(
            f"<div class='terminal-block'><p style='color:#5ce1e6; font-family:JetBrains Mono; margin-bottom:0.4rem;'>VECTOR DE RECONOCIMIENTO:</p>{st.session_state.morph_analysis}</div>",
            unsafe_allow_html=True
        )
        if st.session_state.encoded_image:
            st.image(f"data:image/jpeg;base64,{st.session_state.encoded_image}", caption="Proyección Isométrica Analizada", use_container_width=True)

    with res_col2:
        st.markdown("<div class='sub-tech'>// SÍNTESIS PROFÉTICO-TEÓRICA</div>", unsafe_allow_html=True)
        st.markdown("### Exégesis de la Geometría Unificada")
        st.markdown(
            f"<div class='terminal-block' style='border-left-color: #5ce1e6;'><div style='white-space: pre-wrap; font-family:Inter;'>{st.session_state.prophecy_thesis}</div></div>",
            unsafe_allow_html=True
        )
