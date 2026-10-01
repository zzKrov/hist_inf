import os
import io
import base64
import numpy as np
from PIL import Image
import streamlit as st
from streamlit_drawable_canvas import st_canvas
from openai import OpenAI

# -----------------------------------------------------------------------------
# CONFIGURACIÓN DEL ENTORNO
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Tesseract // Entorno de Análisis Geométrico",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded"
)

DEFAULT_API_KEY = os.getenv(
    "OPENAI_API_KEY",
    "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"
)

# Inicialización de estado
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
# ESTILOS CSS: ARQUITECTURA VISUAL SÓBRIA, MODERNA Y MINIMALISTA
# -----------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;700&family=Inter:wght@300;400;500;600;700&display=swap');

:root {
    --bg-dark: #0a0c10;
    --panel-bg: rgba(15, 18, 26, 0.7);
    --border-subtle: rgba(255, 255, 255, 0.08);
    --border-accent: rgba(200, 160, 80, 0.35);
    --brass: #c5a059;
    --brass-glow: rgba(197, 160, 89, 0.15);
    --cyan-dim: #7da5c9;
    --text-primary: #e6ebf2;
    --text-secondary: #8792a2;
}

.stApp {
    background-color: var(--bg-dark);
    background-image: 
        radial-gradient(at 0% 0%, rgba(20, 26, 40, 0.5) 0px, transparent 50%),
        radial-gradient(at 100% 100%, rgba(15, 18, 28, 0.6) 0px, transparent 50%);
    color: var(--text-primary);
    font-family: 'Inter', -apple-system, sans-serif;
}

/* Tipografía de control */
.tech-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--brass);
}

.tech-header {
    font-family: 'Inter', sans-serif;
    font-weight: 600;
    letter-spacing: -0.02em;
    color: var(--text-primary);
}

/* Indicadores de Fase (3 Módulos) */
.pipeline-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    margin: 1rem 0 1.6rem 0;
}

.pipeline-card {
    background: var(--panel-bg);
    border: 1px solid var(--border-subtle);
    border-radius: 8px;
    padding: 1rem 1.2rem;
    position: relative;
    backdrop-filter: blur(16px);
    transition: border-color 0.25s ease, box-shadow 0.25s ease;
}

.pipeline-card:hover {
    border-color: var(--border-accent);
    box-shadow: 0 4px 20px var(--brass-glow);
}

.pipeline-card.active {
    border-color: var(--brass);
    background: linear-gradient(180deg, rgba(25, 30, 44, 0.85) 0%, rgba(15, 18, 26, 0.95) 100%);
    box-shadow: 0 0 18px rgba(197, 160, 89, 0.12);
}

.pipeline-card .card-step {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    color: var(--brass);
    margin-bottom: 0.25rem;
}

.pipeline-card .card-title {
    font-size: 0.92rem;
    font-weight: 600;
    color: var(--text-primary);
}

.pipeline-card .card-desc {
    font-size: 0.78rem;
    color: var(--text-secondary);
    margin-top: 0.25rem;
    line-height: 1.4;
}

/* Lienzo tipo Workstation */
div[data-testid="stCanvas"] {
    border-radius: 12px !important;
    border: 1px solid var(--border-subtle) !important;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5) !important;
    margin: 0 auto;
    background: #0d0f14;
}

div[data-testid="stCanvas"] canvas {
    cursor: crosshair !important;
}

/* Paneles de datos generados */
.output-module {
    background: rgba(13, 16, 23, 0.85);
    border: 1px solid var(--border-subtle);
    border-left: 2px solid var(--brass);
    border-radius: 6px;
    padding: 1.25rem;
    font-size: 0.9rem;
    line-height: 1.65;
}

/* Canvas de partículas sutil de fondo */
#micro-mesh {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    pointer-events: none;
    z-index: 9999;
}
</style>

<canvas id="micro-mesh"></canvas>
<script>
// Sistema de estela micrométrica para precisión visual
const canvas = document.getElementById('micro-mesh');
if (canvas) {
    const ctx = canvas.getContext('2d');
    let points = [];
    
    function setSize() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }
    setSize();
    window.addEventListener('resize', setSize);
    
    window.addEventListener('mousemove', (e) => {
        points.push({
            x: e.clientX,
            y: e.clientY,
            life: 1.0
        });
    });
    
    function draw() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        for(let i = 0; i < points.length; i++) {
            let p = points[i];
            ctx.fillStyle = `rgba(197, 160, 89, ${p.life * 0.35})`;
            ctx.fillRect(p.x, p.y, 1.5, 1.5);
            p.life -= 0.04;
            if (p.life <= 0) {
                points.splice(i, 1);
                i--;
            }
        }
        requestAnimationFrame(draw);
    }
    draw();
}
</script>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# BARRA LATERAL: SUITE DE INSTRUMENTACIÓN (KRITA / CAD STYLE)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("<div class='tech-label'>// PARÁMETROS DEL SISTEMA</div>", unsafe_allow_html=True)
    st.markdown("#### Configuración de Captura")
    
    with st.expander("Clave de Acceso al Motor", expanded=False):
        api_key = st.text_input(
            "API Key",
            type="password",
            value=DEFAULT_API_KEY,
            help="Clave preconfigurada para inferencia visual."
        )
    
    st.markdown("---")
    st.markdown("<div class='tech-label'>HERRAMIENTA DE TRAZADO</div>", unsafe_allow_html=True)
    
    tools = {
        "Trazo continuo (Freedraw)": "freedraw",
        "Segmento rectilíneo (Line)": "line",
        "Marco ortogonal (Rect)": "rect",
        "Proyección elíptica (Circle)": "circle",
        "Manipulación de vector": "transform"
    }
    selected_tool = st.radio("Herramienta activa", list(tools.keys()), index=0, label_visibility="collapsed")
    draw_mode = tools[selected_tool]
    
    st.markdown("---")
    st.markdown("<div class='tech-label'>CALIBRE Y GEOMETRÍA</div>", unsafe_allow_html=True)
    stroke_width = st.slider("Calibre de trazo (px)", min_value=1, max_value=25, value=3)
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        stroke_color = st.color_picker("Tinta de vector", "#e6ebf2")
    with col_c2:
        fill_active = st.checkbox("Relleno", value=False)
        fill_color_hex = st.color_picker("Color", "#1a2130")
    
    fill_color = fill_color_hex + "44" if fill_active else "rgba(0,0,0,0)"
    bg_canvas = st.color_picker("Fondo del plano", "#0d0f14")

    st.markdown("---")
    if st.button("Restablecer Plano", use_container_width=True):
        st.session_state.canvas_epoch += 1
        st.session_state.pipeline_step = 1
        st.session_state.structural_id = ""
        st.session_state.theoretical_model = ""
        st.session_state.image_buffer = ""
        st.rerun()

# -----------------------------------------------------------------------------
# CABECERA Y PIPELINE DE ESTADO (3 BLOQUES TÉCNICOS)
# -----------------------------------------------------------------------------
col_h1, col_h2 = st.columns([0.8, 0.2])
with col_h1:
    st.markdown("<h2 class='tech-header' style='margin:0;'>PROYECTO TESSERACT // SISTEMA DE MODELADO FORMAL</h2>", unsafe_allow_html=True)
    st.markdown("<div class='tech-label'>Topología gráfica aplicada y deducción mecanicista de sistemas</div>", unsafe_allow_html=True)
with col_h2:
    st.markdown("<div style='text-align:right; font-family:JetBrains Mono; font-size:0.85rem; color:#8792a2; padding-top:0.5rem;'>SYS.REV.04</div>", unsafe_allow_html=True)

# Estado de las 3 fases
step1_status = "active" if st.session_state.pipeline_step == 1 else ""
step2_status = "active" if st.session_state.pipeline_step == 2 else ""
step3_status = "active" if st.session_state.pipeline_step >= 3 else ""

st.markdown(f"""
<div class="pipeline-grid">
    <div class="pipeline-card {step1_status}">
        <div class="card-step">ETAPA 01 // ENTRADA</div>
        <div class="card-title">Diagramación Vectorial</div>
        <div class="card-desc">Inscripción formal del esquema bidimensional en el plano de proyección.</div>
    </div>
    <div class="pipeline-card {step2_status}">
        <div class="card-step">ETAPA 02 // PARSING</div>
        <div class="card-title">Clasificación Estructural</div>
        <div class="card-desc">Extracción de morfología, balance axial y topología de contornos.</div>
    </div>
    <div class="pipeline-card {step3_status}">
        <div class="card-step">ETAPA 03 // PROYECCIÓN</div>
        <div class="card-title">Formulación Teórica</div>
        <div class="card-desc">Deducción de principios físicos y arquitectura del sistema subyacente.</div>
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# LIENZO DE TRABAJO (MAXIMIZADO)
# -----------------------------------------------------------------------------
canvas_result = st_canvas(
    fill_color=fill_color,
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color=bg_canvas,
    height=480,
    width=980,
    drawing_mode=draw_mode,
    key=f"engine_canvas_{st.session_state.canvas_epoch}",
    display_toolbar=True
)

# -----------------------------------------------------------------------------
# EJECUCIÓN DEL ANÁLISIS EN MEMORIA
# -----------------------------------------------------------------------------
col_b1, col_b2, col_b3 = st.columns([1, 2, 1])
with col_b2:
    process_action = st.button("EJECUTAR ANÁLISIS DE SISTEMA", use_container_width=True, type="primary")

def serialize_canvas_to_base64(canvas_data):
    """Codificación limpia en memoria sin tocar el sistema de archivos."""
    arr = np.array(canvas_data.astype('uint8'))
    image = Image.fromarray(arr).convert('RGB')
    buf = io.BytesIO()
    image.save(buf, format="JPEG", quality=88)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

if process_action:
    if canvas_result.image_data is not None:
        pixel_array = np.array(canvas_result.image_data)[:, :, :3]
        if np.std(pixel_array) < 1.0:
            st.info("El plano se encuentra desprovisto de trazos. Ingrese un esquema antes de ejecutar.")
        else:
            with st.spinner("Procesando estructura vectorial y deduciendo geometría de acoplamiento..."):
                try:
                    b64_image = serialize_canvas_to_base64(canvas_result.image_data)
                    st.session_state.image_buffer = b64_image
                    client = OpenAI(api_key=api_key)

                    # Fase 1: Identificación sobria del dibujo
                    ident_prompt = (
                        "Identifica de forma estrictamente técnica, objetiva y precisa qué representa este dibujo o diagrama. "
                        "Describe únicamente los componentes geométricos o la figura representada en máximo dos oraciones en español. "
                        "No agregues comentarios interpretativos."
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
                        max_tokens=150,
                        temperature=0.1
                    )
                    
                    id_result = id_response.choices[0].message.content.strip()
                    st.session_state.structural_id = id_result
                    st.session_state.pipeline_step = 2

                    # Fase 2: Formulación científica especulativa y predictiva
                    # Se integran de forma puramente matemática e implícita los principios
                    # de equilibrio polar, orden constructivo universal y límites geométricos.
                    theory_prompt = f"""
                    Boceto registrado: '{id_result}'.

                    Desarrolla una formulación física y mecanicista especulativa en español que interprete este boceto como el diagrama técnico de un sistema de frontera o un modelo cosmológico unificado.

                    Pautas estrictas de estilo:
                    - Tono: Monografía académica de investigación avanzada, frío, riguroso, formal y preciso.
                    - Asume que la geometría del boceto codifica una solución a un problema de ingeniería fundamental o a una ley de conservación (distribución de tensiones, dinámica de vórtices, acoplamiento de simetrías o transferencia de momento).
                    - Integra de manera estrictamente IMPLÍCITA y natural los siguientes principios estructurales:
                      1. La existencia de una arquitectura organizativa coherente que subyace a la aparente entropía de la materia.
                      2. El equilibrio dinámico entre dos fuerzas opuestas y complementarias necesarias para estabilizar cualquier macroestructura (tensión/compresión, potencial positivo/negativo).
                      3. Los límites de demarcación geométrica como condición necesaria para que la forma se mantenga coherente en el espacio-tiempo.
                    - PROHIBIDO el uso de jerga mística, esotérica, poética o infantil. No menciones templos, símbolos, magia ni analogías sobrenaturales. Debe leerse como un informe técnico de física teórica prospectiva.
                    
                    Organiza la exposición bajo las siguientes cabeceras exactas:
                    1. CONFIGURACIÓN DEL SISTEMA Y LÍMITES GEOMÉTRICOS
                    2. MECÁNICA DE ACOPLAMIENTO Y EQUILIBRIO DE FUERZAS
                    3. PROYECCIÓN PREDICTIVA DE COMPORTAMIENTO
                    """

                    theory_response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {
                                "role": "system",
                                "content": "Actúas como un investigador en física de sistemas complejos y teoría de campos unificados. Tu redacción es formal, aséptica y matemáticamente estructurada."
                            },
                            {"role": "user", "content": theory_prompt}
                        ],
                        max_tokens=650,
                        temperature=0.4
                    )

                    st.session_state.theoretical_model = theory_response.choices[0].message.content
                    st.session_state.pipeline_step = 3

                except Exception as err:
                    st.error(f"Fallo durante la evaluación teórica: {err}")

# -----------------------------------------------------------------------------
# DESPLIEGUE DE RESULTADOS TÉCNICOS
# -----------------------------------------------------------------------------
if st.session_state.structural_id:
    st.markdown("---")
    col_out1, col_out2 = st.columns([1, 2.2])

    with col_out1:
        st.markdown("<div class='tech-label'>// DETERMINACIÓN FORMAL</div>", unsafe_allow_html=True)
        st.markdown("### Clasificación de Entrada")
        st.markdown(
            f"""
            <div class='output-module'>
                <div style='font-family:JetBrains Mono; font-size:0.75rem; color:#8792a2; margin-bottom:0.4rem;'>VECTOR PRIMARIO:</div>
                <div>{st.session_state.structural_id}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.session_state.image_buffer:
            st.image(
                f"data:image/jpeg;base64,{st.session_state.image_buffer}",
                caption="Plano geométrico procesado",
                use_container_width=True
            )

    with col_out2:
        st.markdown("<div class='tech-label'>// DEDUCCIÓN MECANICISTA</div>", unsafe_allow_html=True)
        st.markdown("### Formulación del Sistema y Modelo Teórico")
        st.markdown(
            f"""
            <div class='output-module' style='border-left-color: var(--brass);'>
                <div style='white-space: pre-wrap; font-size:0.88rem;'>{st.session_state.theoretical_model}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
