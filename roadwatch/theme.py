"""Look and feel: asphalt, lane markings and road-sign colours."""
from __future__ import annotations

import streamlit as st

from roadwatch.signs import warning_sign

TEXT, MUTED = "#F2F2F2", "#A7AFBD"
AMBER, RED, GREEN, BLUE = "#FFC400", "#FF4D3D", "#2ED47A", "#4DA3FF"
OUTCOME_COLORS = {"Accident": RED, "No accident": BLUE}

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700&family=Barlow:wght@400;500;600&display=swap');
html, body, .stApp { font-family: 'Barlow', 'Segoe UI', Arial, sans-serif; }
.stApp {
  background:
    radial-gradient(900px 480px at 100% -5%, rgba(255,196,0,.08) 0%, rgba(255,196,0,0) 62%),
    radial-gradient(700px 420px at -5% 30%, rgba(77,163,255,.07) 0%, rgba(77,163,255,0) 60%),
    #14161B;
}
#MainMenu, footer { visibility: hidden; }
.block-container { padding-top: 2.2rem; max-width: 1180px; }
h1, h2, h3, h4 { font-family: 'Barlow Condensed', 'Arial Narrow', sans-serif !important; letter-spacing: .01em; }
[data-testid="stSidebar"] { background: #101216; border-right: 3px dashed rgba(255,196,0,.65); }
.stButton > button { border-radius: 8px; border: 2px solid #FFC400; background: transparent; color: #FFC400; font-weight: 600; }
.stButton > button:hover { background: #FFC400; color: #14161B; border-color: #FFC400; }
[data-testid="stMetric"] { background: #1F232B; border: 1px solid #343A46; border-left: 5px solid #FFC400; border-radius: 8px; padding: 12px 16px; }
.stTabs [data-baseweb="tab"] { font-weight: 600; }

.brand { display: flex; align-items: center; gap: 10px; padding: 4px 4px 14px 4px; }
.brand-name { font-family: 'Barlow Condensed', sans-serif; font-size: 1.6rem; font-weight: 700; line-height: 1; color: #F2F2F2; }
.brand-sub { font-size: .85rem; color: #A7AFBD; }
.side-foot { font-size: .82rem; color: #A7AFBD; padding-top: 10px; line-height: 1.5; }

.page-title { font-family: 'Barlow Condensed', sans-serif; font-size: clamp(2.1rem, 4.2vw, 3.2rem); font-weight: 700; line-height: 1.05; color: #F2F2F2; }
.page-sub { color: #A7AFBD; font-size: 1.08rem; margin-top: 6px; max-width: 64ch; }
.lane { height: 5px; width: 170px; margin: 14px 0 24px 0; background: repeating-linear-gradient(90deg, #FFC400 0 26px, transparent 26px 44px); }

.callout { display: flex; gap: 14px; align-items: center; background: rgba(255,196,0,.09); border-left: 5px solid #FFC400; border-radius: 0 10px 10px 0; padding: 12px 16px; margin: 6px 0 18px 0; color: #E8E3D0; font-size: .98rem; line-height: 1.45; }
.callout svg { flex: none; }

.hero { position: relative; display: grid; grid-template-columns: 1.15fr .85fr; gap: 12px; align-items: end; border-radius: 16px; overflow: hidden; background: linear-gradient(180deg, #0D0F14 0%, #1A1E27 100%); padding: 40px 40px 0 44px; border: 1px solid #2B313C; margin-bottom: 20px; }
.hero-title { font-family: 'Barlow Condensed', sans-serif; font-weight: 700; text-transform: uppercase; color: #FFFFFF; font-size: clamp(2.3rem, 5vw, 4rem); line-height: .98; letter-spacing: .01em; }
.hero-sub { color: #B8C0CE; font-size: 1.1rem; margin: 16px 0 34px 0; max-width: 46ch; line-height: 1.5; }
.hero-signs { display: flex; justify-content: center; align-items: flex-end; gap: 26px; }
.post { display: flex; flex-direction: column; align-items: center; }
.pole { width: 6px; background: linear-gradient(90deg, #6B7280, #9CA3AF, #6B7280); }
.road { grid-column: 1 / -1; position: relative; height: 70px; margin: 0 -40px 0 -44px; background: #2A2D34; border-top: 4px solid #F2F2F2; overflow: hidden; }
.road::after { content: ''; position: absolute; left: 0; right: 0; top: 50%; height: 6px; transform: translateY(-50%); background: repeating-linear-gradient(90deg, #FFC400 0 40px, transparent 40px 80px); animation: roll 1.4s linear infinite; }
@keyframes roll { from { background-position: 0 0; } to { background-position: -80px 0; } }
@media (prefers-reduced-motion: reduce) { .road::after { animation: none; } }
@media (max-width: 820px) { .hero { grid-template-columns: 1fr; padding: 28px 22px 0 22px; } .road { margin: 0 -22px 0 -22px; } .hero-signs { padding-bottom: 6px; } }

.signs-row { display: flex; flex-wrap: wrap; gap: 34px; margin: 6px 0 12px 0; }
.stat { text-align: center; max-width: 150px; }
.stat-cap { color: #A7AFBD; font-size: .92rem; margin-top: 4px; line-height: 1.3; }

.verdict { display: flex; gap: 22px; align-items: center; background: #1F232B; border: 1px solid #343A46; border-left: 8px solid var(--c); border-radius: 12px; padding: 18px 22px; }
.verdict-pct { font-family: 'Barlow Condensed', sans-serif; font-size: 3.6rem; font-weight: 700; line-height: 1; color: var(--c); }
.verdict-title { font-family: 'Barlow Condensed', sans-serif; font-size: 1.5rem; font-weight: 700; color: #F2F2F2; margin-top: 2px; }
.verdict-sub { color: #A7AFBD; font-size: .95rem; line-height: 1.4; margin-top: 4px; }
.meter { position: relative; height: 14px; border-radius: 4px; margin: 26px 0 6px 0; background: linear-gradient(90deg, #2ED47A 0 var(--base), #FFC400 var(--base) 50%, #FF4D3D 50% 100%); }
.meter i { position: absolute; top: -9px; width: 0; height: 0; margin-left: -9px; border-left: 9px solid transparent; border-right: 9px solid transparent; border-top: 14px solid #FFFFFF; }
.meter-scale { display: flex; justify-content: space-between; color: #A7AFBD; font-size: .8rem; }
.factor { display: flex; align-items: center; gap: 10px; padding: 8px 12px; margin: 6px 0; background: #1F232B; border: 1px solid #2B313C; border-radius: 8px; font-size: .96rem; }
.factor .arrow { font-size: .8rem; }
.factor .val { color: #A7AFBD; }
.factor .pts { margin-left: auto; font-weight: 600; }
.up { color: #FF4D3D; } .down { color: #2ED47A; }

.rule-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }
.rule-card { display: flex; gap: 18px; align-items: center; background: #1F232B; border: 1px solid #2B313C; border-radius: 12px; padding: 16px 18px; }
.rule-card svg { flex: none; }
.rule-title { font-family: 'Barlow Condensed', sans-serif; font-size: 1.35rem; font-weight: 700; color: #F2F2F2; }
.rule-text { color: #B8C0CE; font-size: .96rem; line-height: 1.45; margin-top: 2px; }
@media (max-width: 820px) { .rule-grid { grid-template-columns: 1fr; } .verdict { flex-direction: column; text-align: center; } }
</style>
"""


def html(s: str) -> None:
    """Render raw HTML (whitespace collapsed so Markdown never breaks it)."""
    st.markdown(" ".join(s.split()), unsafe_allow_html=True)


def inject_css() -> None:
    html(CSS)


def sidebar_brand() -> None:
    with st.sidebar:
        html(f'<div class="brand">{warning_sign("!", 46)}<div><div class="brand-name">Road Watch</div>'
             f'<div class="brand-sub">Accident risk predictor</div></div></div>')
        html('<div class="side-foot">Random Forest &amp; Decision Tree<br>scikit-learn &middot; Streamlit<br>'
             'A learning project, not a safety tool.</div>')


def page_header(title: str, subtitle: str) -> None:
    html(f'<div class="page-title">{title}</div><div class="page-sub">{subtitle}</div><div class="lane"></div>')


def callout(text: str) -> None:
    html(f'<div class="callout">{warning_sign("!", 44)}<div>{text}</div></div>')


def style_fig(fig, height=380, title=None):
    layout = dict(template="plotly_dark",
                  font=dict(family="Barlow, Segoe UI, Arial, sans-serif", color=TEXT),
                  paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.03)",
                  margin=dict(l=10, r=10, t=50 if title else 20, b=10), height=height,
                  legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0))
    if title:
        layout["title"] = dict(text=title, x=0.0)
    fig.update_layout(**layout)
    return fig


def show_chart(fig) -> None:
    """Full-width chart (stretches by default in Streamlit 1.50+)."""
    st.plotly_chart(fig)
