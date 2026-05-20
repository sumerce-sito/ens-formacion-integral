import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go
import random, time, base64, os
from data import (
    CAFFAREL_QUOTES, HISTORY_EVENTS, OBLIGATIONS, GLOSSARY,
    QUIZ_QUESTIONS, CLOZE_TESTS, CASOS, MAESTRIA_QUESTIONS,
    BADGES, REFLECTION_PROMPTS,
)

# ── Logo ──────────────────────────────────────────
_LOGO_PATH = os.path.join(os.path.dirname(__file__), "LOGO ENS.png")
def _b64_img(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()
LOGO_B64 = _b64_img(_LOGO_PATH) if os.path.exists(_LOGO_PATH) else None

# ── Page config ───────────────────────────────────
st.set_page_config(
    page_title="ENS — Formación Integral",
    page_icon="⚜️",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ── Confetti helpers ──────────────────────────────
def confetti(duration=3):
    components.html(f"""
    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.9.2/dist/confetti.browser.min.js"></script>
    <script>
    var end = Date.now() + {duration}*1000;
    var colors = ['#ffd700','#1a2744','#c9a227','#ffffff','#4fc3f7','#ef5350'];
    (function frame(){{
        confetti({{particleCount:4,angle:60,spread:55,origin:{{x:0}},colors:colors}});
        confetti({{particleCount:4,angle:120,spread:55,origin:{{x:1}},colors:colors}});
        if(Date.now()<end) requestAnimationFrame(frame);
    }}());
    </script>""", height=1)

def confetti_burst():
    components.html("""
    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.9.2/dist/confetti.browser.min.js"></script>
    <script>
    confetti({particleCount:250,spread:120,origin:{y:0.5},
              colors:['#ffd700','#1a2744','#c9a227','#fff','#ff6b6b','#4fc3f7']});
    setTimeout(()=>confetti({particleCount:150,spread:90,origin:{y:0.3},angle:60}),400);
    setTimeout(()=>confetti({particleCount:150,spread:90,origin:{y:0.3},angle:120}),800);
    </script>""", height=1)

# ── Session state init ────────────────────────────
def init_state():
    defaults = {
        "points": 0,
        "badges": set(),
        "quiz_done": False,
        "quiz_pct": 0,
        "adivina_score": 0, "adivina_total": 0, "adivina_idx": 0,
        "adivina_answered": False,
        "adivina_order": random.sample(range(len(HISTORY_EVENTS)), len(HISTORY_EVENTS)),
        "cloze_score": 0, "cloze_total": 0, "cloze_idx": 0,
        "cloze_answered": False, "cloze_order": list(range(len(CLOZE_TESTS))),
        "caso_idx": 0, "caso_score": 0, "caso_answered": False,
        "rayo_active": False, "rayo_score": 0, "rayo_total": 0,
        "rayo_end": 0, "rayo_qs": [], "rayo_idx": 0,
        "card_idx": 0, "card_flipped": False, "card_known": 0,
        "card_order": list(range(len(GLOSSARY))),
        "maestria_done": False, "maestria_pct": 0,
        "comp_checks": {i: False for i in range(len(OBLIGATIONS))},
        "reflection_idx": 0,
        "quote_idx": 0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ── Badge award helper ────────────────────────────
def award(key, pts=0):
    if key not in st.session_state.badges:
        st.session_state.badges.add(key)
        st.session_state.points += BADGES[key]["pts"]
        b = BADGES[key]
        st.toast(f"{b['icon']} ¡Insignia desbloqueada! {b['name']}", icon="🏅")
    if len(st.session_state.badges) >= len(BADGES) - 1 and "experto" not in st.session_state.badges:
        award("experto")

# ── CSS ───────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Lato:wght@300;400;700&display=swap');
html,body,[class*="css"]{font-family:'Lato',sans-serif;}

/* Sidebar */
[data-testid="stSidebar"]{background:linear-gradient(180deg,#0d1a35 0%,#1a2744 50%,#243460 100%);}
[data-testid="stSidebar"] *{color:#f0e6c8!important;}
[data-testid="stSidebar"] .stRadio label{font-size:1rem;padding:5px 0;cursor:pointer;transition:all .2s;}
[data-testid="stSidebar"] .stRadio label:hover{color:#ffd700!important;padding-left:6px!important;}
.main .block-container{background:#faf8f4;padding-top:1.5rem;max-width:1120px;}

/* Animations */
@keyframes fadeInDown{from{opacity:0;transform:translateY(-25px)}to{opacity:1;transform:translateY(0)}}
@keyframes fadeInUp  {from{opacity:0;transform:translateY(25px)} to{opacity:1;transform:translateY(0)}}
@keyframes shimmer   {0%{background-position:-200% center}100%{background-position:200% center}}
@keyframes pulse     {0%,100%{transform:scale(1)}50%{transform:scale(1.04)}}
@keyframes float     {0%,100%{transform:translateY(0)}50%{transform:translateY(-8px)}}
@keyframes glow      {0%,100%{box-shadow:0 0 8px rgba(255,215,0,.3)}50%{box-shadow:0 0 22px rgba(255,215,0,.7)}}
@keyframes spin      {from{transform:rotate(0deg)}to{transform:rotate(360deg)}}
@keyframes countdown {from{stroke-dashoffset:0}to{stroke-dashoffset:283}}

/* Hero */
.hero{background:linear-gradient(135deg,#1a2744 0%,#243460 45%,#1a4f7a 100%);
      border-radius:18px;padding:48px 40px;text-align:center;margin-bottom:28px;
      position:relative;overflow:hidden;animation:fadeInDown .8s ease-out;}
.hero::before{content:'';position:absolute;inset:0;
  background:linear-gradient(90deg,transparent,rgba(255,215,0,.05),transparent);
  background-size:200% 100%;animation:shimmer 3s infinite;}
.hero-title   {font-family:'Playfair Display',serif;font-size:2.8rem;font-weight:700;color:#ffd700;margin:0;text-shadow:2px 2px 8px rgba(0,0,0,.4);}
.hero-sub     {font-size:1.2rem;color:#c8d8f0;margin-top:10px;font-weight:300;}
.hero-badge   {display:inline-block;background:rgba(255,215,0,.15);border:1px solid rgba(255,215,0,.4);border-radius:30px;padding:5px 18px;color:#ffd700;font-size:.85rem;margin-top:14px;}

/* Section title */
.sec-title{font-family:'Playfair Display',serif;font-size:1.9rem;color:#1a2744;
           border-bottom:3px solid #ffd700;padding-bottom:7px;margin:26px 0 16px;animation:fadeInDown .6s ease-out;}
.sec-sub  {font-size:1rem;color:#4a5568;margin-bottom:18px;font-style:italic;}

/* Cards */
.card{background:white;border-radius:14px;padding:20px 22px;margin-bottom:14px;
      border-left:5px solid #1a2744;box-shadow:0 3px 14px rgba(0,0,0,.08);
      transition:transform .2s,box-shadow .2s;animation:fadeInUp .5s ease-out;}
.card:hover{transform:translateY(-3px);box-shadow:0 8px 24px rgba(0,0,0,.12);}
.card.gold {border-left-color:#c9a227;} .card.blue{border-left-color:#1a4f7a;} .card.green{border-left-color:#2d7a4f;}
.card h3{color:#1a2744;font-family:'Playfair Display',serif;margin-top:0;}
.card p {color:#4a5568;margin:0;line-height:1.7;}

/* Stats */
.stat-row{display:flex;gap:14px;margin:18px 0;flex-wrap:wrap;}
.stat-box{background:linear-gradient(135deg,#1a2744,#243460);color:white;border-radius:14px;
          padding:18px 22px;flex:1;min-width:130px;text-align:center;}
.stat-num  {font-size:2.1rem;font-weight:700;color:#ffd700;}
.stat-label{font-size:.82rem;color:#c8d8f0;margin-top:3px;}

/* Badge cards */
.badge-card{background:white;border-radius:12px;padding:16px;text-align:center;
            box-shadow:0 3px 12px rgba(0,0,0,.09);transition:transform .2s;}
.badge-card:hover{transform:translateY(-3px);}
.badge-card.earned{background:linear-gradient(135deg,#fffbeb,#fef3c7);border:2px solid #ffd700;}
.badge-card.locked{opacity:.45;filter:grayscale(.6);}
.badge-icon {font-size:2rem;margin-bottom:6px;}
.badge-name {font-weight:700;color:#1a2744;font-size:.88rem;}
.badge-desc {font-size:.75rem;color:#6b7280;margin-top:3px;}
.badge-pts  {background:#1a2744;color:#ffd700;border-radius:10px;padding:2px 8px;font-size:.72rem;margin-top:5px;display:inline-block;}

/* Progress bar */
.pb-bg{background:#e2e8f0;border-radius:10px;height:16px;overflow:hidden;margin:10px 0;}
.pb-fill{background:linear-gradient(90deg,#1a2744,#ffd700);height:100%;border-radius:10px;transition:width .5s ease;}

/* Pillar grid */
.pillar-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:14px;margin:18px 0;}
.pillar-card{background:linear-gradient(135deg,#1a2744,#243460);color:white;border-radius:14px;
             padding:22px;text-align:center;transition:transform .2s;}
.pillar-card:hover{transform:translateY(-4px) scale(1.02);}
.p-icon{font-size:2.3rem;margin-bottom:8px;animation:float 3s ease-in-out infinite;display:block;}
.p-title{font-family:'Playfair Display',serif;font-size:1.15rem;color:#ffd700;margin-bottom:6px;}
.p-text {font-size:.88rem;color:#c8d8f0;line-height:1.6;}

/* Timeline */
.timeline{position:relative;padding-left:28px;}
.timeline::before{content:'';position:absolute;left:7px;top:0;bottom:0;width:3px;
                  background:linear-gradient(to bottom,#ffd700,#1a2744);border-radius:3px;}
.tl-item{position:relative;margin-bottom:24px;animation:fadeInUp .5s ease-out;}
.tl-dot {position:absolute;left:-23px;top:5px;width:13px;height:13px;border-radius:50%;
         background:#ffd700;border:3px solid #1a2744;animation:glow 2s ease-in-out infinite;}
.tl-year{font-weight:700;color:#1a2744;font-size:1rem;}
.tl-text{color:#4a5568;margin-top:3px;line-height:1.6;}
.tl-detail{color:#6b7280;font-size:.88rem;font-style:italic;margin-top:2px;}

/* Step / obligation */
.step{display:flex;align-items:flex-start;gap:14px;background:white;border-radius:12px;
      padding:16px 18px;margin-bottom:10px;box-shadow:0 2px 10px rgba(0,0,0,.07);
      transition:transform .2s;}
.step:hover{transform:translateX(4px);}
.step-num{background:linear-gradient(135deg,#1a2744,#243460);color:#ffd700;border-radius:50%;
          width:36px;height:36px;display:flex;align-items:center;justify-content:center;
          font-weight:700;font-size:.95rem;flex-shrink:0;}
.step h4{color:#1a2744;margin:0 0 3px;}
.step p {color:#4a5568;margin:0;font-size:.93rem;}

/* Quiz / game */
.qcard{background:white;border-radius:16px;padding:26px 28px;box-shadow:0 4px 18px rgba(0,0,0,.10);
       margin-bottom:18px;border-top:4px solid #1a2744;}
.qtxt{font-size:1.1rem;font-weight:700;color:#1a2744;margin-bottom:16px;}
.res-ok  {background:linear-gradient(135deg,#d4edda,#c3e6cb);border:1px solid #28a745;border-radius:10px;padding:13px 16px;color:#155724;font-weight:600;margin-top:10px;}
.res-bad {background:linear-gradient(135deg,#f8d7da,#f5c6cb);border:1px solid #dc3545;border-radius:10px;padding:13px 16px;color:#721c24;font-weight:600;margin-top:10px;}
.score-badge{background:linear-gradient(135deg,#1a2744,#243460);color:#ffd700;border-radius:16px;
             padding:22px 30px;text-align:center;font-size:1.3rem;font-weight:700;
             animation:pulse 2s ease-in-out infinite;margin:18px 0;}

/* Flashcard */
.fc-front{background:linear-gradient(135deg,#1a2744,#243460);color:white;border-radius:16px;
          padding:40px 28px;text-align:center;min-height:150px;display:flex;align-items:center;
          justify-content:center;font-size:1.25rem;font-weight:700;}
.fc-back {background:linear-gradient(135deg,#2d7a4f,#3a9a65);color:white;border-radius:16px;
          padding:28px;min-height:150px;font-size:.97rem;line-height:1.75;}


/* Blockquote */
.bq{background:linear-gradient(135deg,#f8f4ec,#fff9f0);border-left:5px solid #c9a227;
    border-radius:0 12px 12px 0;padding:18px 22px;margin:18px 0;font-style:italic;
    color:#3a3020;font-size:1.02rem;line-height:1.8;}
.bq cite{display:block;font-style:normal;font-weight:700;color:#1a2744;margin-top:8px;}

/* Org chart */
.org-level{display:flex;justify-content:center;gap:10px;margin-bottom:6px;flex-wrap:wrap;}
.org-box{background:linear-gradient(135deg,#1a2744,#243460);color:white;border-radius:9px;
         padding:9px 16px;font-size:.82rem;text-align:center;min-width:115px;
         border:2px solid rgba(255,215,0,.3);transition:all .2s;cursor:pointer;}
.org-box:hover{border-color:#ffd700;transform:scale(1.05);}
.org-title{color:#ffd700;font-weight:700;font-size:.78rem;}
.org-desc {color:#c8d8f0;font-size:.72rem;margin-top:2px;}
.org-arr  {text-align:center;color:#1a2744;font-size:1.4rem;margin:1px 0;opacity:.5;}

/* Rayo timer */
.rayo-timer{background:linear-gradient(135deg,#1a2744,#8B0000);color:white;border-radius:14px;
            padding:20px;text-align:center;font-size:2.5rem;font-weight:700;color:#ffd700;}

/* ── Mobile-first responsive ── */
.main .block-container{padding-left:1rem!important;padding-right:1rem!important;max-width:100%!important;}

@media (max-width: 768px) {
  /* Hero */
  .hero{padding:28px 18px!important;}
  .hero-title{font-size:1.7rem!important;}
  .hero-sub{font-size:.95rem!important;}
  .hero-badge{font-size:.78rem!important;}

  /* Section titles */
  .sec-title{font-size:1.4rem!important;}

  /* Pillar grid: 1 column on mobile */
  .pillar-grid{grid-template-columns:1fr!important;}

  /* Stats: wrap tightly */
  .stat-row{gap:8px!important;}
  .stat-box{min-width:100px!important;padding:12px 10px!important;}
  .stat-num{font-size:1.6rem!important;}

  /* Cards */
  .card{padding:14px 16px!important;}

  /* Flashcard */
  .fc-front,.fc-back{padding:24px 16px!important;font-size:1rem!important;}

  /* Rayo timer */
  .rayo-timer{font-size:1.8rem!important;padding:14px!important;}

  /* Quiz card */
  .qcard{padding:18px 16px!important;}

  /* Org chart: allow horizontal scroll */
  .org-level{flex-wrap:nowrap!important;overflow-x:auto!important;}

  /* Steps */
  .step{padding:12px 14px!important;}
  .step-num{width:30px!important;height:30px!important;font-size:.82rem!important;}

  /* Score badge */
  .score-badge{font-size:1rem!important;padding:16px 18px!important;}

  /* Streamlit columns stacking on mobile */
  [data-testid="column"]{min-width:100%!important;flex:100%!important;}

  /* Sidebar button (hamburger) bigger tap target */
  [data-testid="collapsedControl"]{padding:10px!important;}

  /* Metrics smaller */
  [data-testid="stMetric"]{padding:8px!important;}
  [data-testid="stMetricValue"]{font-size:1.1rem!important;}
}

@media (max-width: 480px) {
  .hero-title{font-size:1.4rem!important;}
  .hero-sub{font-size:.85rem!important;}
  .stat-num{font-size:1.3rem!important;}
  .sec-title{font-size:1.2rem!important;}
}
</style>
""", unsafe_allow_html=True)

# ── Navigation options (global so buttons outside sidebar can use them) ──
PAGES = [
    "— APRENDER —",
    "🗺️ Mi Ruta ENS",
    "📜 Historia",
    "⚖️ La Carta",
    "✨ Mística y Espíritu",
    "🏛️ Estructura y Roles",
    "📅 Reunión Mensual",
    "— PRACTICAR —",
    "✍️ Completar la Frase",
    "🎯 Casos Prácticos",
    "⚡ Modo Relámpago",
    "🃏 Tarjetas de Memoria",
    "🧠 Quiz Interactivo",
    "— EVALUAR —",
    "🏆 Test de Maestría",
    "— HERRAMIENTAS —",
    "📋 Mis Compromisos",
    "📖 Glosario",
]
HEADERS = {"— APRENDER —", "— PRACTICAR —", "— EVALUAR —", "— HERRAMIENTAS —"}
NAV_OPTS = [p for p in PAGES if p not in HEADERS]
if "nav_idx" not in st.session_state:
    st.session_state.nav_idx = 0

# ── Sidebar ───────────────────────────────────────
with st.sidebar:
    if LOGO_B64:
        st.markdown(f"""
        <div style="text-align:center;padding:14px 0 4px;">
            <div style="display:flex;align-items:center;justify-content:center;
                        background:white;border-radius:14px;padding:10px 16px;
                        box-shadow:0 2px 12px rgba(0,0,0,.3);">
                <img src="data:image/png;base64,{LOGO_B64}"
                     style="width:130px;max-width:80%;display:block;margin:0 auto;" />
            </div>
            <div style="font-size:.72rem;color:#a0b4d0;margin-top:8px;letter-spacing:.06em;text-transform:uppercase;">
                Formación Integral</div>
        </div>
        <hr style="border-color:rgba(255,215,0,.2);margin:6px 0 12px;">
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align:center;padding:18px 0 8px;">
            <div style="font-size:2.8rem;">⚜️</div>
            <div style="font-family:'Playfair Display',serif;font-size:1.05rem;color:#ffd700;font-weight:700;">
                Equipos de<br>Nuestra Señora</div>
            <div style="font-size:.75rem;color:#a0b4d0;margin-top:4px;">Formación Integral</div>
        </div>
        <hr style="border-color:rgba(255,215,0,.2);margin:8px 0 14px;">
        """, unsafe_allow_html=True)

    pts = st.session_state.points
    nb  = len(st.session_state.badges)
    st.markdown(f"""
    <div style="background:rgba(255,215,0,.1);border-radius:10px;padding:10px 14px;margin-bottom:14px;text-align:center;">
        <span style="color:#ffd700;font-weight:700;font-size:1.1rem;">⭐ {pts} pts</span>
        <span style="color:#c8d8f0;font-size:.85rem;margin-left:10px;">🏅 {nb}/{len(BADGES)} insignias</span>
    </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div style="background:rgba(255,215,0,.12);border:1px solid rgba(255,215,0,.35);
                border-radius:10px;padding:9px 12px;margin-bottom:10px;font-size:.82rem;
                color:#ffd700;text-align:center;line-height:1.5;">
        👆 Toca una sección para navegar
    </div>""", unsafe_allow_html=True)

    # Inyectar CSS para los separadores de sección dentro del radio
    st.markdown("""
    <style>
    div[data-testid="stSidebar"] .stRadio div[role="radiogroup"] { gap: 0; }
    </style>""", unsafe_allow_html=True)

    active = st.radio("Navegación", NAV_OPTS, label_visibility="collapsed",
                      index=st.session_state.nav_idx,
                      format_func=lambda x: x,
                      key="main_nav_radio")
    st.session_state.nav_idx = NAV_OPTS.index(active)

# ── Global helpers ────────────────────────────────
def hero(title, subtitle, badge=""):
    b = f'<div class="hero-badge">{badge}</div>' if badge else ""
    st.markdown(f'<div class="hero"><div class="hero-title">{title}</div><div class="hero-sub">{subtitle}</div>{b}</div>', unsafe_allow_html=True)

def card(text, title="", variant=""):
    h = f"<h3>{title}</h3>" if title else ""
    st.markdown(f'<div class="card {variant}">{h}<p>{text}</p></div>', unsafe_allow_html=True)

def bq(text, author=""):
    a = f"<cite>— {author}</cite>" if author else ""
    st.markdown(f'<div class="bq">{text}{a}</div>', unsafe_allow_html=True)


def progress_bar(val, total):
    pct = int(val/total*100) if total else 0
    st.markdown(f'<div class="pb-bg"><div class="pb-fill" style="width:{pct}%"></div></div>', unsafe_allow_html=True)
    return pct

# ════════════════════════════════════════════════════════
#  🗺️  MI RUTA ENS — Dashboard de aprendizaje
# ════════════════════════════════════════════════════════
if active == "🗺️ Mi Ruta ENS":
    # Logo + title centered at the top of the landing page
    if LOGO_B64:
        st.markdown(f"""
        <div style="text-align:center;margin-bottom:10px;">
            <img src="data:image/png;base64,{LOGO_B64}"
                 style="width:180px;filter:drop-shadow(0 4px 16px rgba(26,39,68,.25));" />
        </div>""", unsafe_allow_html=True)
    hero("Mi Ruta ENS", "Tu panel de progreso hacia convertirte en experto del movimiento", "⚜️ Basado en la Carta y la Guía de los ENS")

    # ── Puntos y nivel ──────────────────────────────
    pts = st.session_state.points
    nivel_txt = ("🌱 Iniciado" if pts < 50 else "📖 Conocedor" if pts < 150
                 else "🎓 Formado" if pts < 300 else "⭐ Experto ENS")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("⭐ Puntos totales", pts)
    col2.metric("🏅 Insignias", f"{len(st.session_state.badges)}/{len(BADGES)}")
    col3.metric("📊 Nivel", nivel_txt)
    col4.metric("🎯 Casos resueltos", st.session_state.caso_score)

    st.markdown(f"""
    <div class="pb-bg" style="height:22px;">
      <div class="pb-fill" style="width:{min(pts,500)/500*100:.0f}%;"></div>
    </div>
    <p style="text-align:center;color:#4a5568;font-size:.9rem;">{pts}/500 pts hacia Experto ENS</p>
    """, unsafe_allow_html=True)

    # ── Ruta de aprendizaje visual ──────────────────
    st.markdown('<div class="sec-title">🗺️ Ruta de Aprendizaje</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">Avanza paso a paso: desde conocer el movimiento hasta dominarlo como experto.</div>', unsafe_allow_html=True)

    rutas = [
        ("1","📜 Historia","Conoce el origen, el fundador y la cronología del movimiento.","historiador"),
        ("2","⚖️ La Carta","Estudia el documento fundacional, sus principios y obligaciones.","guardian"),
        ("3","✍️ Completar la Frase","Demuestra que conoces el texto exacto de la Carta.","guardian"),
        ("4","🎯 Casos Prácticos","Resuelve situaciones reales usando la Carta como guía.","decisor"),
        ("5","⚡ Modo Relámpago","Velocidad y precisión: responde 15 preguntas en 60 segundos.","velocista"),
        ("6","🃏 Tarjetas de Memoria","Memoriza los 18 conceptos clave del glosario ENS.","memorizador"),
        ("7","🧠 Quiz Interactivo","Quiz integral de todos los temas del movimiento.","conocedor"),
        ("8","🏆 Test de Maestría","El examen final: 20 preguntas profundas para el experto.","maestro"),
    ]
    for num, sec, desc, badge_key in rutas:
        done = badge_key in st.session_state.badges
        color = "#2d7a4f" if done else "#1a2744"
        check = "✅" if done else "⬜"
        col_txt, col_btn = st.columns([5, 1])
        with col_txt:
            st.markdown(f"""
            <div class="step" style="border-left:5px solid {color};margin-bottom:4px;">
                <div class="step-num" style="background:{color};">{num}</div>
                <div>
                    <h4 style="margin:0 0 2px;">{check} {sec}</h4>
                    <p style="margin:0;color:#4a5568;font-size:.9rem;">{desc}</p>
                </div>
            </div>""", unsafe_allow_html=True)
        with col_btn:
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            if st.button("Ir →", key=f"ruta_btn_{num}"):
                st.session_state.nav_idx = NAV_OPTS.index(sec)
                st.rerun()

    # ── Insignias ───────────────────────────────────
    st.markdown('<div class="sec-title">🏅 Mis Insignias</div>', unsafe_allow_html=True)
    cols = st.columns(4)
    for i, (key, b) in enumerate(BADGES.items()):
        earned = key in st.session_state.badges
        css = "earned" if earned else "locked"
        with cols[i % 4]:
            st.markdown(f"""
            <div class="badge-card {css}">
                <div class="badge-icon">{b['icon']}</div>
                <div class="badge-name">{b['name']}</div>
                <div class="badge-desc">{b['desc']}</div>
                <div class="badge-pts">+{b['pts']} pts</div>
            </div>""", unsafe_allow_html=True)

    # ── Metodología ─────────────────────────────────
    st.markdown('<div class="sec-title">📐 Metodología de Aprendizaje</div>', unsafe_allow_html=True)
    card("Esta app propone una <b>ruta progresiva de aprendizaje</b>: comenzar conociendo la historia y la Carta, luego practicar con ejercicios concretos, y finalmente evaluar el dominio con el Test de Maestría. Cada etapa construye sobre la anterior.", "Ruta Progresiva de Aprendizaje")
    cols2 = st.columns(3)
    with cols2[0]:
        card("Las tarjetas de memoria y el quiz aplican <b>Evocación Activa</b>: recuperar información del recuerdo es 3× más efectivo que releerla.", "Evocación Activa", "gold")
    with cols2[1]:
        card("Los Casos Prácticos usan <b>Aprendizaje Basado en Escenarios</b> (Knowles): los adultos aprenden mejor cuando el contenido es inmediatamente aplicable.", "Aprendizaje por Escenarios", "blue")
    with cols2[2]:
        card("Las insignias y los puntos aplican <b>Gamificación</b>: combinar repetición con recompensas produce retención 3× mayor que solo lectura pasiva.", "Gamificación", "green")

# ════════════════════════════════════════════════════════
#  📜  HISTORIA
# ════════════════════════════════════════════════════════
elif active == "📜 Historia":
    hero("Historia de los ENS", "Del primer encuentro en París al movimiento de miles de familias en el mundo", "📜 Desde 1938 — Fundado por el P. Henri Caffarel")

    tab1, tab2, tab3 = st.tabs(["📅 Cronología", "🎯 Adivina el Año", "👤 El Fundador"])

    with tab1:
        st.markdown('<div class="sec-title">Línea del Tiempo del Movimiento</div>', unsafe_allow_html=True)
        st.markdown('<div class="timeline">', unsafe_allow_html=True)
        for ev in HISTORY_EVENTS:
            st.markdown(f"""
            <div class="tl-item">
                <div class="tl-dot"></div>
                <div class="tl-year">⚑ {ev['year']}</div>
                <div class="tl-text">{ev['event']}</div>
                <div class="tl-detail">↳ {ev['detail']}</div>
            </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Gráfica de hitos clave
        fig = go.Figure()
        years = [e["year"] for e in HISTORY_EVENTS]
        labels = [str(e["year"]) for e in HISTORY_EVENTS]
        fig.add_trace(go.Scatter(
            x=years, y=[1]*len(years), mode="markers+text",
            marker=dict(size=18, color="#ffd700", line=dict(color="#1a2744", width=3)),
            text=labels, textposition="top center",
            hovertext=[e["event"] for e in HISTORY_EVENTS], hoverinfo="text",
        ))
        fig.update_layout(
            height=200, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#faf8f4",
            xaxis=dict(showgrid=False, zeroline=False),
            yaxis=dict(visible=False), margin=dict(t=40,b=10),
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.markdown('<div class="sec-title">🎯 Adivina el Año</div>', unsafe_allow_html=True)
        st.markdown("Lee el evento histórico y selecciona el año correcto. ¡Pon a prueba tu memoria!")

        col_s, col_p = st.columns(2)
        with col_s:
            st.metric("Puntuación", f"{st.session_state.adivina_score}/{st.session_state.adivina_total}")
        with col_p:
            pct_a = progress_bar(st.session_state.adivina_idx, len(HISTORY_EVENTS))
            st.caption(f"Pregunta {min(st.session_state.adivina_idx+1, len(HISTORY_EVENTS))} de {len(HISTORY_EVENTS)}")

        if st.session_state.adivina_idx < len(HISTORY_EVENTS):
            ev = HISTORY_EVENTS[st.session_state.adivina_order[st.session_state.adivina_idx]]
            st.markdown(f'<div class="qcard"><div class="qtxt">"{ev["event"]}"</div></div>', unsafe_allow_html=True)

            # Generate options once per question and lock them in session_state
            opts_key = f"adivina_opts_{st.session_state.adivina_idx}"
            if opts_key not in st.session_state:
                all_yrs = [e["year"] for e in HISTORY_EVENTS]
                wrongs = random.sample([y for y in all_yrs if y != ev["year"]], 3)
                st.session_state[opts_key] = sorted(wrongs + [ev["year"]])
            opts = st.session_state[opts_key]

            if not st.session_state.adivina_answered:
                sel = st.radio("Año:", [str(y) for y in opts], horizontal=True, key=f"a_{st.session_state.adivina_idx}")
                if st.button("✅ Confirmar", key="adivina_confirm"):
                    st.session_state.adivina_total += 1
                    st.session_state.adivina_answered = True
                    st.session_state.adivina_correct = (int(sel) == ev["year"])
                    if st.session_state.adivina_correct:
                        st.session_state.adivina_score += 1
                        st.session_state.points += 5
                    st.rerun()
            else:
                if st.session_state.adivina_correct:
                    st.markdown(f'<div class="res-ok">✅ ¡Correcto! +5 pts</div>', unsafe_allow_html=True)
                    confetti(1)
                else:
                    st.markdown(f'<div class="res-bad">❌ Era <strong>{ev["year"]}</strong> — {ev["detail"]}</div>', unsafe_allow_html=True)
                if st.button("➡️ Siguiente"):
                    st.session_state.adivina_idx += 1
                    st.session_state.adivina_answered = False
                    st.rerun()
        else:
            pct_f = int(st.session_state.adivina_score / len(HISTORY_EVENTS) * 100)
            st.markdown(f'<div class="score-badge">🏁 {st.session_state.adivina_score}/{len(HISTORY_EVENTS)} · {pct_f}%</div>', unsafe_allow_html=True)
            if pct_f >= 70:
                award("historiador")
                confetti_burst()
            if st.button("🔄 Jugar de nuevo"):
                st.session_state.adivina_idx = 0; st.session_state.adivina_score = 0
                st.session_state.adivina_total = 0; st.session_state.adivina_answered = False
                st.session_state.adivina_order = random.sample(range(len(HISTORY_EVENTS)), len(HISTORY_EVENTS))
                for k in list(st.session_state.keys()):
                    if k.startswith("adivina_opts_"):
                        del st.session_state[k]
                st.rerun()

    with tab3:
        st.markdown('<div class="sec-title">Padre Henri Caffarel (1903–1996)</div>', unsafe_allow_html=True)
        col1, col2 = st.columns([2,1])
        with col1:
            card("Henri Caffarel nació en Lyon en 1903. Ordenado sacerdote en 1930, respondió en 1938 a cuatro parejas que buscaban orientación con las palabras <b>'¡Busquemos juntos!'</b> — el inicio de un movimiento que llegaría a millones de hogares.", "Sacerdote y Fundador")
            card("Caffarel comprendió que el matrimonio cristiano era una vocación real de santidad y que las parejas necesitaban apoyo comunitario estructurado: <em>'No una regla de monjes, sino una regla para laicos casados.'</em>", "Su Visión", "gold")
            card("Falleció el 18 de septiembre de 1996 a los 93 años. El Cardenal Lustiger: <em>'Una de las grandes figuras regaladas por Dios a su Iglesia a lo largo de este siglo.'</em> Su causa de beatificación fue abierta en 2006.", "Su Legado", "blue")
        with col2:
            st.markdown("""
            <div style="background:linear-gradient(135deg,#1a2744,#243460);border-radius:14px;padding:22px;color:white;text-align:center;">
                <div style="font-size:3rem;animation:float 3s ease-in-out infinite;display:block;margin-bottom:10px;">✝️</div>
                <div style="font-family:'Playfair Display',serif;color:#ffd700;font-size:1.05rem;">P. Henri Caffarel</div>
                <div style="color:#c8d8f0;font-size:.83rem;margin-top:8px;line-height:2;">
                    🏠 Lyon, 1903<br>⛪ Ordenado, 1930<br>⚜️ Fundó ENS, 1938<br>✝️ Falleció, 1996
                    <hr style="border-color:rgba(255,215,0,.3);margin:10px 0;">
                    <span style="color:#ffd700;">Beatificación</span><br>
                    <span style="font-size:.78rem;">Proceso abierto 2006</span>
                </div>
            </div>""", unsafe_allow_html=True)
        bq("Debo reconocer que, en la creación de los equipos, hubo algo más que mi propia inspiración.", "Padre Henri Caffarel")

# ════════════════════════════════════════════════════════
#  ⚖️  LA CARTA
# ════════════════════════════════════════════════════════
elif active == "⚖️ La Carta":
    hero("La Carta de los ENS", "El documento fundacional promulgado el 8 de diciembre de 1947", "Piedra angular del movimiento · La 'Regla' de los ENS")

    tab1, tab2, tab3 = st.tabs(["📄 Contenido Esencial", "📋 Las 9 Obligaciones", "📚 Documentos del Movimiento"])

    with tab1:
        card("La Carta es el documento de referencia vital del Movimiento. Escrita en 1947 bajo la inspiración del Padre Caffarel, define lo esencial de la 'Regla' de los ENS. Miles de parejas a través del mundo descubren en su matrimonio la riqueza del profundo amor de Dios.")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Las parejas de los ENS se proponen:")
            for p in ["Permanecer fieles a las promesas de su bautismo","Poner a Jesucristo en el centro de sus vidas","Basar la vida conyugal en el Evangelio","Comunicar el mensaje de Cristo al mundo","Dar testimonio de valores cristianos en lo social y profesional","Promover el matrimonio y la vida de familia","Caminar al lado de la Iglesia con apoyo activo"]:
                st.markdown(f"- {p}")
        with col2:
            card("La palabra <b>Equipo</b> implica una finalidad precisa, perseguida activamente y en común. No son guarderías de adultos, sino una fuerza de choque formada por voluntarios.", "¿Por qué 'Equipo'?")
            card("Los Equipos están bajo el patrocinio de <b>Nuestra Señora</b> para subrayar la voluntad de servirla y la certeza de que Ella es el mejor guía hacia Dios.", "¿Por qué 'Nuestra Señora'?", "gold")
        bq("Sus Equipos no son guarderías de adultos de 'buena voluntad', sino una fuerza de choque formada por voluntarios. Nadie está obligado a ingresar ni a permanecer. Pero los que ingresan deben seguir el juego noblemente.", "La Carta, 1947")

    with tab2:
        st.markdown('<div class="sec-title">Las 9 Obligaciones de la Carta</div>', unsafe_allow_html=True)
        for icon, name, letter, desc in OBLIGATIONS:
            with st.expander(f"{icon} Obligación {letter.upper()}: {name}"):
                st.markdown(f"<p style='color:#4a5568;line-height:1.8;'>{desc}</p>", unsafe_allow_html=True)
                # Mini visual para cada obligación
                freq = {"a":"Continua","b":"Diaria","c":"Diaria","d":"Mensual","e":"Mensual","f":"Mensual","g":"Anual","h":"Anual","i":"Ocasional"}
                st.markdown(f'<span style="background:#1a2744;color:#ffd700;padding:3px 10px;border-radius:10px;font-size:.78rem;">📅 Frecuencia: {freq.get(letter,"—")}</span>', unsafe_allow_html=True)

    with tab3:
        docs = [
            ("📄","La Carta (1947)","Piedra angular. Define el espíritu, la mística y la disciplina del movimiento.","Obligatoria"),
            ("📋","¿Qué es un Equipo? (1977)","Redefine el ideal y los métodos con presentación actualizada. Desarrolla el equipo como comunidad.","Referencia"),
            ("🎙️","Conferencia de Chantilly (1987)","El P. Caffarel señala aspectos menos percibidos: abnegación, sexualidad cristiana, misión.","Referencia"),
            ("💨","El Segundo Aliento (1988)","Ayuda a los equipos a encontrar nuevas razones de motivación espiritual.","Complementario"),
            ("🌐","Guía de los ENS (2001/2018)","Guía completa actualizada para el siglo XXI y la Nueva Evangelización.","Vigente"),
            ("📜","Vocación y Misión (2018)","Fruto sinodal. Responde al llamado del Papa Francisco hacia la Nueva Evangelización.","Vigente"),
        ]
        for i, (ico, tit, desc, tag) in enumerate(docs):
            tag_css = "background:#1a2744;color:#ffd700;" if tag=="Obligatoria" else "background:#2d7a4f;color:white;" if tag=="Vigente" else "background:#c9a227;color:white;"
            st.markdown(f"""
            <div class="card {'gold' if i%2==0 else 'blue'}">
                <h3>{ico} {tit} <span style="{tag_css}padding:2px 8px;border-radius:8px;font-size:.72rem;">{tag}</span></h3>
                <p>{desc}</p>
            </div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════
#  ✨  MÍSTICA Y ESPÍRITU
# ════════════════════════════════════════════════════════
elif active == "✨ Mística y Espíritu":
    hero("Mística y Espíritu", "Los fundamentos espirituales que dan vida y sostienen al movimiento", "✨ Fe · Oración · Amor · Testimonio")

    tab1, tab2, tab3 = st.tabs(["🤝 Los Tres Pilares", "✝️ Testimonio", "💭 Reflexión para Parejas"])

    with tab1:
        st.markdown('<div class="sec-sub">La mística y la regla, lo mismo que el alma y el cuerpo, no pueden prescindir una de la otra.</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            card("<b>1. Fe y Estudio:</b> No hay vida cristiana sin fe viva; no hay fe viva sin reflexión. Los matrimonios se esfuerzan conjuntamente en profundizar su conocimiento religioso y ajustar su vida a las exigencias de Cristo.", "Fe Viva y Reflexión")
            card("<b>2. Oración:</b> Al estudio hay que añadir la oración. Los equipos se ayudan a orar: ruegan los unos con los otros, los unos por los otros. 'Donde dos o tres se reúnan en mi nombre, allí estoy yo.' (Mt 18,20)", "Oración en Común", "blue")
            card("<b>3. Ayuda Fraterna:</b> La vida espiritual no florece si no se superan las preocupaciones cotidianas. Los hogares practican la ayuda mutua en lo material y lo moral. 'Llevad los unos las cargas de los otros.' (Gál 6,2)", "Ayuda Mutua", "gold")
        with col2:
            fig2 = go.Figure(go.Scatterpolar(
                r=[9,9,9,9], theta=["Fe y Estudio","Oración","Ayuda Mutua","Fe y Estudio"],
                fill="toself", fillcolor="rgba(26,39,68,.2)",
                line=dict(color="#ffd700",width=3),
            ))
            fig2.update_layout(polar=dict(radialaxis=dict(visible=False),angularaxis=dict(tickfont=dict(size=13))),
                               showlegend=False, height=300, paper_bgcolor="rgba(0,0,0,0)",margin=dict(t=20,b=20))
            st.plotly_chart(fig2, use_container_width=True)
            st.markdown('<div class="pillar-grid">', unsafe_allow_html=True)
            for ico, ttl, txt in [("🙏","Espiritualidad","Oración personal, conyugal y comunitaria"),("🤝","Fraternidad","Apoyo real en todos los planos de la vida"),("📚","Formación","Estudio conjunto del pensamiento cristiano"),("✝️","Misión","Testimonio en la Iglesia y en el mundo")]:
                st.markdown(f'<div class="pillar-card"><span class="p-icon">{ico}</span><div class="p-title">{ttl}</div><div class="p-text">{txt}</div></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        card("Los primeros cristianos eran admirados: <em>'Eran un solo corazón y una sola alma.'</em> Decían al verlos: <em>'¡Mirad cómo se aman!'</em> y la admiración conducía a la adhesión. Los ENS creen que hoy, lo mismo que entonces, se conquistarán incrédulos para Cristo si ven a matrimonios que se aman verdaderamente.")
        st.markdown('<div class="pillar-grid">', unsafe_allow_html=True)
        for ico, ttl, txt in [("💑","Amor Auténtico","El amor conyugal santificado es el primer testimonio visible"),("👨‍👩‍👧‍👦","Vida Familiar","Una familia centrada en el Evangelio irradia luz"),("🌟","Caridad Fraterna","El amor entre las parejas, visible para el mundo, atrae"),("🕊️","Misión","Ser misioneros del matrimonio en lo profesional y social")]:
            st.markdown(f'<div class="pillar-card"><span class="p-icon">{ico}</span><div class="p-title">{ttl}</div><div class="p-text">{txt}</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        bq("¿Habrá perdido la caridad fraterna en el siglo XXI el poder de seducción que tenía en los primeros tiempos? Los ENS creen que no.", "La Carta, 1947")

    with tab3:
        st.markdown('<div class="sec-title">💭 Generador de Reflexión para Parejas</div>', unsafe_allow_html=True)
        st.markdown("Una pregunta profunda para el Deber de Sentarse o la oración conyugal:")
        idx_r = st.session_state.reflection_idx
        prompt = REFLECTION_PROMPTS[idx_r % len(REFLECTION_PROMPTS)]
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#1a2744,#243460);border-radius:16px;padding:36px;text-align:center;margin:16px 0;">
            <div style="font-size:2rem;margin-bottom:12px;animation:float 3s ease-in-out infinite;display:block;">💭</div>
            <div style="font-family:'Playfair Display',serif;font-size:1.25rem;color:#ffd700;line-height:1.8;">{prompt}</div>
        </div>""", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Nueva reflexión", use_container_width=True):
                st.session_state.reflection_idx = (idx_r + 1) % len(REFLECTION_PROMPTS)
                st.rerun()
        with col2:
            if st.button("💛 Guardar", use_container_width=True):
                if "saved_r" not in st.session_state: st.session_state.saved_r = []
                if prompt not in st.session_state.saved_r:
                    st.session_state.saved_r.append(prompt)
                st.success("¡Guardada!")
        if "saved_r" in st.session_state and st.session_state.saved_r:
            with st.expander("📌 Mis reflexiones guardadas"):
                for r in st.session_state.saved_r:
                    st.markdown(f"- *{r}*")

# ════════════════════════════════════════════════════════
#  🏛️  ESTRUCTURA Y ROLES
# ════════════════════════════════════════════════════════
elif active == "🏛️ Estructura y Roles":
    hero("Estructura del Movimiento", "La Pareja y el Equipo primero — todo lo demás existe para servirles", "🏛️ Subsidiariedad · Colegialidad · Fraternidad")

    tab1, tab2 = st.tabs(["🗂️ Organigrama", "🎭 Explora los Roles"])

    with tab1:
        st.info("💡 **Pirámide invertida:** En los ENS, la Pareja y el Equipo son el corazón y la base de todo. Las estructuras superiores (Sector, Región, ERI) existen únicamente para **servir y sostener** al equipo y a la pareja, no al revés.", icon="🔺")
        st.markdown("""
        <div style="background:white;border-radius:16px;padding:28px;box-shadow:0 4px 18px rgba(0,0,0,.08);">
        <div class="org-level"><div class="org-box" style="background:linear-gradient(135deg,#2d7a4f,#3a9a65);min-width:260px;"><div class="org-title">💑 La Pareja</div><div class="org-desc">El corazón y razón de ser del movimiento</div></div></div>
        <div class="org-arr">▲ sirve a</div>
        <div class="org-level"><div class="org-box" style="background:linear-gradient(135deg,#1a4f7a,#1a6a9a);"><div class="org-title">⚜️ El Equipo</div><div class="org-desc">4–7 matrimonios + Sacerdote Consiliario</div></div></div>
        <div class="org-arr">▲ sirve a</div>
        <div class="org-level"><div class="org-box"><div class="org-title">Sector</div><div class="org-desc">Hogar de Enlace cuida ~5 equipos</div></div></div>
        <div class="org-arr">▲ sirve a</div>
        <div class="org-level"><div class="org-box"><div class="org-title">Región / Provincia</div><div class="org-desc">Agrupa varios Sectores</div></div></div>
        <div class="org-arr">▲ sirve a</div>
        <div class="org-level"><div class="org-box"><div class="org-title">Super Región</div><div class="org-desc">Agrupa varias Regiones</div></div></div>
        <div class="org-arr">▲ sirve a</div>
        <div class="org-level"><div class="org-box" style="min-width:200px;background:linear-gradient(135deg,#8B0000,#a00000);"><div class="org-title">⚜️ ERI</div><div class="org-desc">Equipo Responsable Internacional · al servicio de todos</div></div></div>
        </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        # Inverted funnel: Pareja at top (widest) → ERI at bottom (narrowest)
        # x values are inverted so Pareja appears as the broad base of the inverted pyramid
        fig3 = go.Figure(go.Funnel(
            y=["💑 La Pareja","⚜️ El Equipo (4-7)","🏘️ Sector (~5 eq.)","📍 Región","🌎 Super Región","🌐 ERI Internacional"],
            x=[30000, 3000, 300, 60, 12, 2],
            customdata=[2, 12, 60, 300, 3000, 30000],
            texttemplate="<b>%{label}</b><br>%{customdata:,} personas",
            marker=dict(color=["#2d7a4f","#1a4f7a","#1a2744","#c9a227","#8B0000","#4a0000"]),
            connector=dict(line=dict(color="rgba(0,0,0,0.1)", width=1)),
        ))
        fig3.update_layout(
            title=dict(text="🔺 Pirámide Invertida — La Pareja es la Base de Todo", font=dict(size=15, color="#1a2744")),
            height=400, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=50, b=10),
        )
        st.plotly_chart(fig3, use_container_width=True)

    with tab2:
        roles = {
            "💑 Pareja del Equipo": ("El corazón del movimiento. Viven las obligaciones de la Carta y dan testimonio en el mundo.",
                ["Regla de vida personal","Oración conyugal diaria","Deber de Sentarse mensual","Asistir a la reunión","Retiro anual"],"#1a4f7a"),
            "⭐ Hogar Responsable": ("Responsable del amor fraterno en el equipo. Coordina, anima y mantiene el vínculo con el Centro.",
                ["Misa entre semana","10 min oración diaria","Preparar la reunión mensual","Enviar reseña mensual","Acompañar a cada pareja"],"#c9a227"),
            "✝️ Sacerdote Consiliario": ("Aporta los principios doctrinales y espirituales. Su presencia es insustituible.",
                ["Aportar doctrina y espiritualidad","Celebrar la Eucaristía con el equipo","Orar por las familias","Acompañar en dificultades"],"#8B0000"),
            "🔗 Hogar de Enlace": ("Cuida ~5 equipos de un Sector. Mantiene el flujo de vida del movimiento.",
                ["Visitar equipos regularmente","Transmitir iniciativas del Centro","Escuchar las necesidades","Organizar encuentros de sector"],"#2d7a4f"),
        }
        for rname, (desc, comps, color) in roles.items():
            with st.expander(f"{rname}"):
                col1, col2 = st.columns([3,1])
                with col1:
                    st.markdown(f"**{desc}**")
                    st.markdown("**Compromisos principales:**")
                    for c in comps: st.markdown(f"✦ {c}")
                with col2:
                    st.markdown(f"""<div style="background:linear-gradient(135deg,{color},#1a2744);border-radius:12px;padding:18px;text-align:center;color:white;"><div style="font-size:2.2rem;">{rname.split()[0]}</div><div style="color:#ffd700;font-weight:700;margin-top:6px;font-size:.85rem;">{rname.split(None,1)[1]}</div></div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════
#  📅  REUNIÓN MENSUAL
# ════════════════════════════════════════════════════════
elif active == "📅 Reunión Mensual":
    hero("La Reunión Mensual", "El corazón de la vida del equipo: oración, compartir, estudio y amistad", "📅 Al menos una vez por mes · La amistad exige el trato")

    tab1, tab2 = st.tabs(["📋 Los 5 Momentos", "🎬 Simula tu Reunión"])

    with tab1:
        pasos = [("🍽️","1. Comida en Común","La reunión inicia con comida compartida, unas veces en un hogar y otras en otro. Como los primeros cristianos: 'partían juntos el pan con alegría y sencillez de corazón.' (Hch 2,46)","Inicio"),
                 ("🙏","2. Oración en Común","Mínimo 15 minutos. Las parejas presentan intenciones, se oran salmos e himnos litúrgicos, y hay silencio contemplativo. 'Donde dos o tres se reúnan en mi nombre, allí estoy yo.' (Mt 18,20)","Oración"),
                 ("💬","3. Puesta en Común","Cada matrimonio dice honestamente si ha observado sus compromisos. Alegrías, penas, éxitos y fracasos — con prudencia y verdadera caridad fraterna, sin impudor.","Participación"),
                 ("📚","4. Cambio de Impresiones","Diálogo profundo sobre el tema de estudio mensual, preparado por todos con reflexiones escritas enviadas días antes al hogar director del mes.","Estudio"),
                 ("✨","5. Cierre y Envío","La reunión cierra con oración. Los esposos se van renovados, con nuevas perspectivas y el apoyo del equipo para el mes que comienza.","Cierre")]
        for ico, tit, desc, tag in pasos:
            st.markdown(f"""<div class="step"><div class="step-num" style="font-size:1.2rem;">{ico}</div><div><h4>{tit} <span style="background:#e8f0ff;color:#1a2744;padding:2px 8px;border-radius:10px;font-size:.73rem;">{tag}</span></h4><p>{desc}</p></div></div>""", unsafe_allow_html=True)
        bq("Los cambios de impresiones solo son fecundos en la medida en que se han preparado.", "La Carta, 1947")

    with tab2:
        st.markdown('<div class="sec-title">🎬 Simulador de Reunión</div>', unsafe_allow_html=True)
        st.markdown("Marca cada momento a medida que ocurre en tu reunión real:")
        sim = [("🍽️","Comida compartida — todos presentes"),("🙏","Oración en común realizada (mín. 15 min)"),("💬","Puesta en común completada honestamente"),("📚","Cambio de impresiones sobre el tema del mes"),("✨","Cierre con oración de envío")]
        done_sim = 0
        for i,(ico,lab) in enumerate(sim):
            c1,c2 = st.columns([1,8])
            with c1: ch = st.checkbox("",value=st.session_state.comp_checks.get(f"sim_{i}",False),key=f"sim_{i}")
            if ch: done_sim += 1
            with c2: st.markdown(f'<div class="step {"done" if ch else ""}"><div class="step-num">{ico}</div><div><p style="margin:0;font-weight:{"700" if ch else "400"};">{lab}</p></div></div>', unsafe_allow_html=True)
        pct_s = progress_bar(done_sim, len(sim))
        st.caption(f"{done_sim}/{len(sim)} momentos · {pct_s}%")
        if done_sim == len(sim):
            confetti_burst()
            st.markdown('<div class="score-badge">🎉 ¡Reunión completada! Que este tiempo dé frutos en cada hogar.</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════
#  ✍️  COMPLETAR LA FRASE
# ════════════════════════════════════════════════════════
elif active == "✍️ Completar la Frase":
    hero("Completar la Frase", "Textos reales de la Carta — completa los espacios y prueba que conoces el documento original", "✍️ 15 ejercicios · Aplicar lo aprendido")
    st.markdown(f'<div class="sec-sub">Nivel cognitivo: <b>Aplicar</b> — recuperas el texto exacto del documento fundacional.</div>', unsafe_allow_html=True)

    col_s, col_p = st.columns(2)
    col_s.metric("Correctas", f"{st.session_state.cloze_score}/{st.session_state.cloze_total}")
    with col_p:
        pct_c = progress_bar(st.session_state.cloze_idx, len(CLOZE_TESTS))
        st.caption(f"Ejercicio {min(st.session_state.cloze_idx+1, len(CLOZE_TESTS))} de {len(CLOZE_TESTS)}")

    if st.session_state.cloze_idx < len(CLOZE_TESTS):
        ct = CLOZE_TESTS[st.session_state.cloze_order[st.session_state.cloze_idx]]
        st.markdown(f"""
        <div class="qcard">
            <div class="qtxt">📜 {ct['text']}</div>
            <div style="color:#6b7280;font-size:.82rem;margin-top:4px;">Fuente: <em>{ct['source']}</em></div>
            <div style="color:#c9a227;font-size:.82rem;margin-top:2px;">💡 Pista: {ct['hint']}</div>
        </div>""", unsafe_allow_html=True)

        if not st.session_state.cloze_answered:
            sel = st.radio("Selecciona la palabra correcta:", ct["opts"], horizontal=True, key=f"cl_{st.session_state.cloze_idx}")
            if st.button("✅ Verificar", key="cloze_v"):
                st.session_state.cloze_total += 1
                st.session_state.cloze_answered = True
                st.session_state.cloze_ok = (sel == ct["blank"])
                if st.session_state.cloze_ok:
                    st.session_state.cloze_score += 1
                    st.session_state.points += 8
                st.rerun()
        else:
            if st.session_state.cloze_ok:
                st.markdown(f'<div class="res-ok">✅ ¡Correcto! +8 pts</div>', unsafe_allow_html=True)
                confetti(1)
            else:
                st.markdown(f'<div class="res-bad">❌ La respuesta correcta es: <b>"{ct["blank"]}"</b></div>', unsafe_allow_html=True)
            if st.button("➡️ Siguiente"):
                st.session_state.cloze_idx += 1
                st.session_state.cloze_answered = False
                st.rerun()
    else:
        pct_f = int(st.session_state.cloze_score / len(CLOZE_TESTS) * 100)
        st.markdown(f'<div class="score-badge">📜 {st.session_state.cloze_score}/{len(CLOZE_TESTS)} correctas · {pct_f}%</div>', unsafe_allow_html=True)
        if st.session_state.cloze_score >= 10:
            award("guardian"); confetti_burst()
        if st.button("🔄 Reiniciar"):
            st.session_state.cloze_idx = 0; st.session_state.cloze_score = 0
            st.session_state.cloze_total = 0; st.session_state.cloze_answered = False
            random.shuffle(st.session_state.cloze_order); st.rerun()

# ════════════════════════════════════════════════════════
#  🎯  CASOS PRÁCTICOS
# ════════════════════════════════════════════════════════
elif active == "🎯 Casos Prácticos":
    hero("Casos Prácticos", "Situaciones reales de la vida ENS — aplica la Carta para resolverlos correctamente", "🎯 10 casos · Analizar · Decidir · Fundamentar")

    col_s, col_p = st.columns(2)
    col_s.metric("Casos correctos", f"{st.session_state.caso_score}/10")
    with col_p:
        pct_ca = progress_bar(st.session_state.caso_idx, len(CASOS))
        st.caption(f"Caso {min(st.session_state.caso_idx+1, len(CASOS))} de {len(CASOS)}")

    if st.session_state.caso_idx < len(CASOS):
        caso = CASOS[st.session_state.caso_idx]
        st.markdown(f"""
        <div class="qcard" style="border-top-color:#c9a227;">
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:14px;">
                <span style="font-size:2rem;">{caso['icono']}</span>
                <div>
                    <div style="font-weight:700;color:#1a2744;font-size:1.1rem;">{caso['titulo']}</div>
                </div>
            </div>
            <div style="background:#f0f4ff;border-radius:10px;padding:16px;margin-bottom:14px;">
                <div style="font-size:.82rem;color:#1a4f7a;font-weight:700;margin-bottom:6px;">📋 SITUACIÓN</div>
                <p style="color:#1a2744;margin:0;line-height:1.75;">{caso['situacion']}</p>
            </div>
            <div class="qtxt">{caso['pregunta']}</div>
        </div>""", unsafe_allow_html=True)

        if not st.session_state.caso_answered:
            sel_c = st.radio("Tu respuesta:", caso["opciones"], key=f"caso_{st.session_state.caso_idx}")
            if st.button("✅ Aplicar la Carta", use_container_width=True):
                st.session_state.caso_answered = True
                st.session_state.caso_ok = (caso["opciones"].index(sel_c) == caso["correcta"])
                if st.session_state.caso_ok:
                    st.session_state.caso_score += 1
                    st.session_state.points += 15
                st.rerun()
        else:
            c_text = caso["opciones"][caso["correcta"]]
            if st.session_state.caso_ok:
                st.markdown(f'<div class="res-ok">✅ ¡Decisión correcta según la Carta! +15 pts</div>', unsafe_allow_html=True)
                confetti(1)
            else:
                st.markdown(f'<div class="res-bad">❌ La respuesta correcta según la Carta es: <b>"{c_text}"</b></div>', unsafe_allow_html=True)
            with st.expander("📖 ¿Qué dice la Carta? (Explicación completa)"):
                st.info(caso["explicacion"])
                st.caption(f"📌 Fuente: *{caso['fuente']}*")
            if st.button("➡️ Siguiente caso", use_container_width=True):
                st.session_state.caso_idx += 1
                st.session_state.caso_answered = False
                st.rerun()
    else:
        pct_cf = int(st.session_state.caso_score / len(CASOS) * 100)
        st.markdown(f'<div class="score-badge">🎯 {st.session_state.caso_score}/{len(CASOS)} casos correctos · {pct_cf}%</div>', unsafe_allow_html=True)
        if st.session_state.caso_score >= 7:
            award("decisor"); confetti_burst()
        if st.button("🔄 Reiniciar casos"):
            st.session_state.caso_idx = 0; st.session_state.caso_score = 0
            st.session_state.caso_answered = False; st.rerun()

# ════════════════════════════════════════════════════════
#  ⚡  MODO RELÁMPAGO
# ════════════════════════════════════════════════════════
elif active == "⚡ Modo Relámpago":
    hero("Modo Relámpago ⚡", "60 segundos · máxima velocidad · máxima concentración", "⚡ Velocidad + Precisión")

    ALL_RAYO = QUIZ_QUESTIONS + [
        {"q": "¿Cuántas reuniones mínimas de preparación necesita un nuevo equipo?", "opts":["1","2","3","5"],"ans":2,"exp":"La Carta dice mínimo 3 reuniones de lectura y comentario de la Carta.","nivel":"Aplicar"},
        {"q": "¿Cuál es el primer tema de los 3 años fundamentales?", "opts":["Fecundidad","Amor y Matrimonio","Caminos de unión con Dios","La familia cristiana"],"ans":1,"exp":"Primer año: Amor y Matrimonio. Segundo: Fecundidad. Tercero: Caminos de unión con Dios.","nivel":"Recordar"},
        {"q": "¿Cuántos matrimonios cuida aproximadamente un Hogar de Enlace?", "opts":["2 equipos","5 equipos","10 equipos","20 equipos"],"ans":1,"exp":"El Hogar de Enlace se ocupa de unos 5 equipos dentro de su Sector.","nivel":"Recordar"},
        {"q": "¿En qué año llegaron los ENS al Brasil?", "opts":["1947","1950","1955","1960"],"ans":1,"exp":"Los ENS llegaron al Brasil en 1950, cruzando por primera vez los océanos.","nivel":"Recordar"},
        {"q": "¿Cuántos minutos mínimo de oración en común en la reunión mensual?", "opts":["5","10","15","20"],"ans":2,"exp":"La Carta establece mínimo quince minutos de oración antes del cambio de impresiones.","nivel":"Recordar"},
    ]

    if not st.session_state.rayo_active:
        st.markdown("""
        <div style="text-align:center;padding:30px;">
            <div style="font-size:4rem;animation:bounce 1s ease-in-out infinite;">⚡</div>
            <div style="font-family:'Playfair Display',serif;font-size:1.5rem;color:#1a2744;margin:16px 0;">¿Estás listo?</div>
            <div style="color:#4a5568;">60 segundos · responde tantas preguntas como puedas · +5 pts por respuesta correcta</div>
        </div>""", unsafe_allow_html=True)
        if st.button("⚡ ¡INICIAR!", use_container_width=True):
            qs = random.sample(ALL_RAYO, min(15, len(ALL_RAYO)))
            st.session_state.rayo_active = True
            st.session_state.rayo_qs = qs
            st.session_state.rayo_idx = 0
            st.session_state.rayo_score = 0
            st.session_state.rayo_total = 0
            st.session_state.rayo_end = time.time() + 60
            st.rerun()
    else:
        remaining = max(0, st.session_state.rayo_end - time.time())
        if remaining <= 0 or st.session_state.rayo_idx >= len(st.session_state.rayo_qs):
            pct_r = int(st.session_state.rayo_score / max(st.session_state.rayo_total,1) * 100)
            st.markdown(f"""
            <div class="score-badge">
                ⚡ Tiempo agotado!<br>
                {st.session_state.rayo_score}/{st.session_state.rayo_total} correctas · {pct_r}%<br>
                <span style="font-size:1rem;color:#c8d8f0;">+{st.session_state.rayo_score*5} pts ganados</span>
            </div>""", unsafe_allow_html=True)
            if st.session_state.rayo_score >= 6:
                award("velocista"); confetti_burst()
            if st.button("🔄 Jugar de nuevo"):
                st.session_state.rayo_active = False; st.rerun()
        else:
            secs = int(remaining)
            col_t, col_s = st.columns([1,2])
            with col_t:
                color = "#2d7a4f" if secs > 30 else "#c9a227" if secs > 15 else "#dc3545"
                st.markdown(f'<div class="rayo-timer" style="background:linear-gradient(135deg,#1a2744,{color});">⏱️ {secs}s</div>', unsafe_allow_html=True)
            with col_s:
                st.metric("Correctas", f"{st.session_state.rayo_score}/{st.session_state.rayo_total}")
                progress_bar(st.session_state.rayo_idx, len(st.session_state.rayo_qs))

            q = st.session_state.rayo_qs[st.session_state.rayo_idx]
            st.markdown(f'<div class="qcard"><div class="qtxt">⚡ {q["q"]}</div></div>', unsafe_allow_html=True)
            for i, opt in enumerate(q["opts"]):
                if st.button(opt, key=f"rayo_{st.session_state.rayo_idx}_{i}", use_container_width=True):
                    st.session_state.rayo_total += 1
                    if i == q["ans"]:
                        st.session_state.rayo_score += 1
                        st.session_state.points += 5
                    st.session_state.rayo_idx += 1
                    st.rerun()

# ════════════════════════════════════════════════════════
#  🃏  TARJETAS DE MEMORIA
# ════════════════════════════════════════════════════════
elif active == "🃏 Tarjetas de Memoria":
    hero("Tarjetas de Memoria", "Aprende los 18 conceptos clave del glosario ENS con flashcards interactivas", "🃏 Voltea · Aprende · Memoriza")

    total_c = len(GLOSSARY)
    idx_c = st.session_state.card_order[st.session_state.card_idx % total_c]
    term, defn = GLOSSARY[idx_c]

    col1, col2, col3 = st.columns(3)
    col1.metric("✅ Aprendidas", st.session_state.card_known)
    col2.metric("📚 Tarjeta", f"{(st.session_state.card_idx%total_c)+1}/{total_c}")
    col3.metric("⭐ Pts acumulados", f"{st.session_state.card_known*3}")
    progress_bar(st.session_state.card_idx % total_c, total_c)

    if not st.session_state.card_flipped:
        st.markdown(f"""
        <div class="fc-front">
            <div>
                <div style="font-size:.8rem;color:#a0b8d0;margin-bottom:10px;letter-spacing:2px;">CONCEPTO ENS</div>
                {term}
                <div style="font-size:.75rem;color:#7090b0;margin-top:14px;">👆 Haz clic en "Voltear" para ver la definición</div>
            </div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="fc-back">
            <div style="font-size:.78rem;color:#a8dfc0;margin-bottom:8px;letter-spacing:2px;">{term}</div>
            {defn}
        </div>""", unsafe_allow_html=True)

    c1,c2,c3,c4 = st.columns(4)
    with c1:
        if st.button("🔄 Voltear", use_container_width=True):
            st.session_state.card_flipped = not st.session_state.card_flipped; st.rerun()
    with c2:
        if st.session_state.card_flipped and st.button("✅ Lo sé", use_container_width=True):
            st.session_state.card_known += 1
            st.session_state.points += 3
            st.session_state.card_idx += 1
            st.session_state.card_flipped = False
            if st.session_state.card_known >= 12: award("memorizador")
            st.rerun()
    with c3:
        if st.session_state.card_flipped and st.button("🔁 Repasar", use_container_width=True):
            st.session_state.card_idx += 1; st.session_state.card_flipped = False; st.rerun()
    with c4:
        if st.button("⏭️ Saltar", use_container_width=True):
            st.session_state.card_idx += 1; st.session_state.card_flipped = False; st.rerun()

    if st.session_state.card_idx > 0 and st.session_state.card_idx % total_c == 0:
        confetti(2)
        st.success("🎉 ¡Vuelta completa al mazo! ¡Sigue practicando!")
    if st.button("🔀 Barajar de nuevo"):
        random.shuffle(st.session_state.card_order); st.session_state.card_idx=0
        st.session_state.card_flipped=False; st.session_state.card_known=0; st.rerun()

# ════════════════════════════════════════════════════════
#  🧠  QUIZ INTERACTIVO
# ════════════════════════════════════════════════════════
elif active == "🧠 Quiz Interactivo":
    hero("Quiz Interactivo", "12 preguntas que cubren toda la Carta y la Guía de los ENS", "🧠 Comprensión integral")

    if "quiz_submitted" not in st.session_state: st.session_state.quiz_submitted = False
    if "quiz_mode" not in st.session_state: st.session_state.quiz_mode = "full"
    if "quiz_sel_qs" not in st.session_state: st.session_state.quiz_sel_qs = list(range(len(QUIZ_QUESTIONS)))
    if "quiz_answers" not in st.session_state: st.session_state.quiz_answers = {}

    c1,c2,c3 = st.columns(3)
    with c1:
        if st.button("🎲 Modo Aleatorio (6)", use_container_width=True):
            st.session_state.quiz_submitted=False; st.session_state.quiz_mode="rand"
            st.session_state.quiz_sel_qs=random.sample(range(len(QUIZ_QUESTIONS)),6)
            st.session_state.quiz_answers={}
    with c2:
        if st.button("📋 Completo (12)", use_container_width=True):
            st.session_state.quiz_submitted=False; st.session_state.quiz_mode="full"
            st.session_state.quiz_sel_qs=list(range(len(QUIZ_QUESTIONS))); st.session_state.quiz_answers={}
    with c3:
        if st.button("🔄 Reiniciar", use_container_width=True):
            st.session_state.quiz_submitted=False; st.session_state.quiz_answers={}

    active_qs = [(i, QUIZ_QUESTIONS[i]) for i in st.session_state.quiz_sel_qs]
    with st.form("quiz_f"):
        for n,(i,q) in enumerate(active_qs):
            st.markdown(f'<div class="qcard"><div class="qtxt">{n+1}. {q["q"]}</div></div>', unsafe_allow_html=True)
            st.session_state.quiz_answers[i] = st.radio("", q["opts"], key=f"qz_{i}", label_visibility="collapsed")
            st.markdown("---")
        if st.form_submit_button("✅ Verificar respuestas", use_container_width=True):
            st.session_state.quiz_submitted = True

    if st.session_state.quiz_submitted:
        correct = sum(1 for i,q in active_qs if st.session_state.quiz_answers.get(i)==q["opts"][q["ans"]])
        total = len(active_qs)
        pct_q = int(correct/total*100)
        st.markdown("## 📊 Resultados")
        for n,(i,q) in enumerate(active_qs):
            ua = st.session_state.quiz_answers.get(i,"")
            ca = q["opts"][q["ans"]]
            ok = ua==ca
            st.markdown(f"**{n+1}. {q['q']}**")
            st.markdown(f'<div class="{"res-ok" if ok else "res-bad"}">{"✅ ¡Correcto!" if ok else f"❌ Era: {ca}"}</div>', unsafe_allow_html=True)
            with st.expander("📖 Explicación"): st.info(q["exp"])
        st.markdown(f'<div class="score-badge">{"⭐"*(pct_q//20)}<br>{correct}/{total} · {pct_q}%</div>', unsafe_allow_html=True)
        if pct_q >= 80:
            award("conocedor"); confetti(3)
        if pct_q == 100: confetti_burst(); st.balloons()
        # Gráfica
        fig_q = go.Figure(go.Bar(x=["Correctas","Incorrectas"],y=[correct,total-correct],
                                  marker_color=["#28a745","#dc3545"],text=[correct,total-correct],textposition="outside"))
        fig_q.update_layout(height=260,paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="#faf8f4",showlegend=False,margin=dict(t=20,b=20))
        st.plotly_chart(fig_q, use_container_width=True)

# ════════════════════════════════════════════════════════
#  🏆  TEST DE MAESTRÍA
# ════════════════════════════════════════════════════════
elif active == "🏆 Test de Maestría":
    hero("Test de Maestría", "20 preguntas profundas — de lo básico a lo experto — sobre toda la doctrina ENS", "🏆 Evaluación final · De principiante a experto")
    st.markdown('<div class="sec-sub">Este test recorre todos los niveles: desde hechos concretos hasta análisis profundo y juicio experto sobre los ENS.</div>', unsafe_allow_html=True)

    if "maestria_sub" not in st.session_state: st.session_state.maestria_sub = False
    if "maestria_ans" not in st.session_state: st.session_state.maestria_ans = {}

    if not st.session_state.maestria_sub:
        st.warning("⚠️ Este es el test final. Completa primero las otras secciones para prepararte bien.")
        with st.form("maestria_f"):
            for n,q in enumerate(MAESTRIA_QUESTIONS):
                nivel_m = ["Recordar","Recordar","Recordar","Recordar","Comprender","Comprender","Comprender","Aplicar","Aplicar","Aplicar","Analizar","Analizar","Analizar","Evaluar","Evaluar","Evaluar","Crear","Crear","Crear","Crear"][n]
                st.markdown(f'<div class="qcard"><div class="qtxt">{n+1}. {q["q"]}</div></div>', unsafe_allow_html=True)
                st.session_state.maestria_ans[n] = st.radio("",q["opts"],key=f"m_{n}",label_visibility="collapsed")
                st.markdown("---")
            if st.form_submit_button("🏆 Enviar Test de Maestría", use_container_width=True):
                st.session_state.maestria_sub = True; st.rerun()
    else:
        correct_m = sum(1 for n,q in enumerate(MAESTRIA_QUESTIONS) if st.session_state.maestria_ans.get(n)==q["opts"][q["ans"]])
        total_m = len(MAESTRIA_QUESTIONS)
        pct_m = int(correct_m/total_m*100)
        st.markdown("## 📊 Resultados del Test de Maestría")
        for n,q in enumerate(MAESTRIA_QUESTIONS):
            nivel_m = ["Recordar","Recordar","Recordar","Recordar","Comprender","Comprender","Comprender","Aplicar","Aplicar","Aplicar","Analizar","Analizar","Analizar","Evaluar","Evaluar","Evaluar","Crear","Crear","Crear","Crear"][n]
            ua = st.session_state.maestria_ans.get(n,"")
            ca = q["opts"][q["ans"]]
            ok = ua==ca
            with st.expander(f"{'✅' if ok else '❌'} Pregunta {n+1}"):
                st.markdown(f"**{q['q']}**")
                st.markdown(f'<div class="{"res-ok" if ok else "res-bad"}">{"✅ Correcto" if ok else f"❌ Era: {ca}"}</div>', unsafe_allow_html=True)
                st.info(q["exp"])
        progress_bar(correct_m, total_m)
        stars_m = "⭐"*(pct_m//20)
        msg_m = ("🌟 ¡EXPERTO ENS! Dominas la Carta y la Guía del movimiento." if pct_m>=90
                 else "🎓 ¡Excelente! Estás muy bien formado en los ENS." if pct_m>=80
                 else "📖 Buen nivel. Repasa los casos prácticos y vuelve." if pct_m>=65
                 else "📚 Sigue estudiando. La profundidad de los ENS vale el esfuerzo.")
        st.markdown(f'<div class="score-badge">{stars_m}<br>{correct_m}/{total_m} · {pct_m}%<br><span style="font-size:.95rem;color:#c8d8f0;">{msg_m}</span></div>', unsafe_allow_html=True)
        if pct_m >= 85:
            award("maestro"); st.session_state.points += pct_m
            confetti_burst(); st.balloons()

        # Resultado por sección temática
        secciones = ["Historia","Historia","Historia","Historia","La Carta","La Carta","La Carta","Obligaciones","Obligaciones","Obligaciones","Estructura","Estructura","Estructura","Mística","Mística","Mística","Síntesis","Síntesis","Síntesis","Síntesis"]
        from collections import defaultdict
        by_sec = defaultdict(lambda:[0,0])
        for n,q in enumerate(MAESTRIA_QUESTIONS):
            sec = secciones[n]
            by_sec[sec][1] += 1
            if st.session_state.maestria_ans.get(n)==q["opts"][q["ans"]]: by_sec[sec][0]+=1
        fig_b = go.Figure(go.Bar(
            x=list(by_sec.keys()),
            y=[v[0]/v[1]*100 for v in by_sec.values()],
            marker_color=["#1a2744","#1a4f7a","#c9a227","#2d7a4f","#8B0000","#6b21a8"],
            text=[f"{v[0]}/{v[1]}" for v in by_sec.values()], textposition="outside",
        ))
        fig_b.update_layout(title="% correcto por sección temática",height=320,
                             paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="#faf8f4",
                             yaxis=dict(range=[0,110]),showlegend=False,margin=dict(t=40,b=20))
        st.plotly_chart(fig_b, use_container_width=True)

        if st.button("🔄 Reiniciar Test de Maestría"):
            st.session_state.maestria_sub=False; st.session_state.maestria_ans={}; st.rerun()

# ════════════════════════════════════════════════════════
#  📋  MIS COMPROMISOS
# ════════════════════════════════════════════════════════
elif active == "📋 Mis Compromisos":
    hero("Mis Compromisos Mensuales", "Seguimiento personal de las 9 obligaciones de la Carta — honestidad ante Dios y ante el equipo", "📋 Marca tu fidelidad mensual")

    done_co = sum(1 for i in range(len(OBLIGATIONS)) if st.session_state.comp_checks.get(i,False))
    pct_co = progress_bar(done_co, len(OBLIGATIONS))
    st.caption(f"{done_co}/{len(OBLIGATIONS)} obligaciones · {pct_co}%")

    for i,(ico,name,letter,desc) in enumerate(OBLIGATIONS):
        c1,c2 = st.columns([1,8])
        with c1: ch = st.checkbox("",value=st.session_state.comp_checks.get(i,False),key=f"co_{i}")
        st.session_state.comp_checks[i] = ch
        with c2:
            bg = "background:linear-gradient(135deg,#d4edda,#c3e6cb);" if ch else "background:white;"
            st.markdown(f"""<div class="step" style="{bg}"><div class="step-num" style="font-size:1.1rem;">{ico}</div>
            <div><h4 style="margin:0 0 3px;">Oblig. {letter.upper()}: {name}</h4><p>{desc[:110]}…</p></div></div>""", unsafe_allow_html=True)

    done_co2 = sum(1 for i in range(len(OBLIGATIONS)) if st.session_state.comp_checks.get(i,False))
    if done_co2 == len(OBLIGATIONS):
        award("comprometido"); confetti_burst()
        st.markdown('<div class="score-badge">🙏 ¡Fidelidad total este mes! Que Dios bendiga tu hogar.</div>', unsafe_allow_html=True)

    # Gráfica donut
    fig_co = go.Figure(go.Pie(values=[done_co2, len(OBLIGATIONS)-done_co2],
                               labels=["Practicadas","Pendientes"],hole=.65,
                               marker_colors=["#1a2744","#e2e8f0"],textinfo="none"))
    fig_co.add_annotation(text=f"{int(done_co2/len(OBLIGATIONS)*100)}%",x=.5,y=.5,font_size=26,
                           showarrow=False,font_color="#1a2744",font_family="Playfair Display")
    fig_co.update_layout(showlegend=True,height=260,paper_bgcolor="rgba(0,0,0,0)",margin=dict(t=10,b=10))
    st.plotly_chart(fig_co, use_container_width=True)
    if st.button("🔄 Nuevo mes"): st.session_state.comp_checks={i:False for i in range(len(OBLIGATIONS))}; st.rerun()

# ════════════════════════════════════════════════════════
#  📖  GLOSARIO
# ════════════════════════════════════════════════════════
elif active == "📖 Glosario":
    hero("Glosario ENS", "18 conceptos y siglas clave del movimiento explicados con claridad", "📖 Referencia siempre disponible")

    search = st.text_input("🔍 Buscar término...", placeholder="Escribe para filtrar...")
    filtered = [(t,d) for t,d in GLOSSARY if search.lower() in t.lower() or search.lower() in d.lower()] if search else GLOSSARY
    if not filtered: st.warning("No se encontraron términos.")
    else:
        for term,defn in filtered:
            with st.expander(f"📌 {term}"):
                st.markdown(f"<p style='color:#4a5568;line-height:1.8;font-size:1rem;'>{defn}</p>", unsafe_allow_html=True)

    st.markdown('<div class="sec-title">Siglas del Movimiento</div>', unsafe_allow_html=True)
    siglas=[("ENS","Equipos de Nuestra Señora","Nombre completo del movimiento"),("ERI","Equipo Responsable Internacional","Máxima autoridad del movimiento"),("HR","Hogar Responsable","Pareja coordinadora del equipo"),("SC","Sacerdote Consiliario","Sacerdote acompañante"),("AAC","Asoc. Amigos del P. Caffarel","Promueve la beatificación del fundador"),("EG","Evangelii Gaudium","Exhortación del Papa Francisco, base del doc. 2018")]
    cols=st.columns(3)
    for i,(s,f,d) in enumerate(siglas):
        with cols[i%3]: st.markdown(f'<div class="card {"gold" if i%3==0 else "blue" if i%3==1 else ""}"><h3 style="color:#c9a227;font-size:1.4rem;">{s}</h3><p><b>{f}</b><br><span style="font-size:.85rem;">{d}</span></p></div>', unsafe_allow_html=True)

    st.markdown('<div class="sec-title">Citas Fundamentales</div>', unsafe_allow_html=True)
    for txt,auth in CAFFAREL_QUOTES:
        bq(txt, auth)
