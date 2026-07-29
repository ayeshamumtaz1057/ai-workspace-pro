"""Refined grey theme with light accents — clean, portal-like look."""
import streamlit as st
from config import THEME as T


def inject_css(font_size: str = "Medium", dark: bool = True) -> None:
    scale = {"Small": "14px", "Medium": "15px", "Large": "17px"}.get(font_size, "15px")

    st.markdown(f"""
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;600&display=swap');

      html, body, [class*="css"] {{ font-family:'Inter',sans-serif; font-size:{scale};
          -webkit-font-smoothing:antialiased; }}

      .stApp {{ background:
          radial-gradient(1100px 500px at 80% -10%, rgba(124,138,160,.10), transparent 60%),
          {T['bg']};
          color:{T['text']}; }}

      section[data-testid="stSidebar"] {{
          background:{T['surface']}; border-right:1px solid {T['border']}; }}
      #MainMenu, footer, header[data-testid="stHeader"] {{ visibility:hidden; }}
      .block-container {{ padding-top:2rem; max-width:1280px; }}

      /* ---- Wordmark ---- */
      .aw-wordmark {{ font-family:'Space Grotesk',sans-serif; font-weight:700;
          font-size:clamp(28px,4.4vw,50px); letter-spacing:.03em; text-align:center;
          background:linear-gradient(90deg,{T['muted']},{T['text']} 50%,{T['accent']});
          -webkit-background-clip:text; -webkit-text-fill-color:transparent; margin:.2rem 0 0; }}
      .aw-sub {{ text-align:center; color:{T['muted']}; letter-spacing:.4em;
          font-size:.68rem; text-transform:uppercase; margin-bottom:1.5rem; }}

      /* ---- Section banner (portal-style header bar) ---- */
      .aw-banner {{ background:linear-gradient(90deg,{T['surface_2']},{T['surface']});
          border:1px solid {T['border']}; border-left:3px solid {T['primary']};
          border-radius:12px; padding:14px 18px; margin-bottom:1rem; }}
      .aw-banner b {{ font-size:1.02rem; color:{T['text']}; }}
      .aw-banner span {{ display:block; font-size:.8rem; color:{T['muted']}; margin-top:2px; }}

      /* ---- Clean feature cards ---- */
      .aw-card {{ background:{T['surface_2']}; border:1px solid {T['border']};
          border-radius:14px; padding:18px 20px; height:100%;
          transition:border-color .18s ease, box-shadow .18s ease, transform .18s ease;
          display:flex; gap:14px; align-items:flex-start; }}
      .aw-card:hover {{ border-color:{T['primary']}; transform:translateY(-2px);
          box-shadow:0 10px 26px rgba(0,0,0,.32); }}
      .aw-card .aw-ico {{ font-size:1.3rem; flex:0 0 auto; width:42px; height:42px;
          display:flex; align-items:center; justify-content:center; border-radius:10px;
          background:{T['surface']}; border:1px solid {T['border']}; }}
      .aw-card .aw-body h4 {{ margin:.1rem 0 .3rem; font-size:.98rem; font-weight:600;
          color:{T['text']}; }}
      .aw-card .aw-body p {{ margin:0; font-size:.82rem; color:{T['muted']}; line-height:1.5; }}

      /* ---- Panels ---- */
      .aw-panel {{ background:{T['surface']}; border:1px solid {T['border']};
          border-radius:14px; padding:16px 18px; }}
      .aw-panel h3 {{ font-size:.74rem; margin:0 0 .8rem; color:{T['muted']};
          letter-spacing:.14em; text-transform:uppercase; font-weight:600; }}
      .aw-row {{ display:flex; justify-content:space-between; align-items:center;
          padding:8px 0; border-bottom:1px solid {T['border']}; font-size:.84rem; }}
      .aw-row:last-child {{ border-bottom:none; }}
      .aw-muted {{ color:{T['muted']}; font-size:.78rem; }}
      .aw-pill {{ display:inline-block; padding:4px 11px; border-radius:999px;
          font-size:.7rem; border:1px solid {T['border']}; color:{T['muted']};
          margin:0 6px 6px 0; background:{T['surface_2']}; }}
      .aw-strip {{ background:{T['surface']}; border:1px solid {T['border']};
          border-radius:12px; padding:13px 15px; }}
      .aw-strip b {{ display:block; font-size:.84rem; color:{T['text']}; margin-top:2px; }}
      .aw-strip span {{ font-size:.73rem; color:{T['muted']}; }}

      /* ---- Controls ---- */
      .stButton>button {{ border-radius:10px; border:1px solid {T['border']};
          background:{T['surface_2']}; color:{T['text']}; font-weight:500;
          transition:all .16s ease; }}
      .stButton>button:hover {{ border-color:{T['primary']}; color:#fff;
          background:{T['primary']}; }}
      .stButton>button[kind="primary"] {{
          background:linear-gradient(90deg,{T['primary']},{T['accent']});
          border:none; color:#12151a; font-weight:600; }}

      .stTextInput input, .stTextArea textarea,
      .stSelectbox div[data-baseweb="select"] > div {{
          background:{T['surface_2']} !important; color:{T['text']} !important;
          border-color:{T['border']} !important; border-radius:10px !important; }}
      .stTextInput input:focus, .stTextArea textarea:focus {{
          border-color:{T['primary']} !important; }}

      [data-testid="stMetric"] {{ background:{T['surface']}; border:1px solid {T['border']};
          border-radius:12px; padding:14px 16px; }}

      .stTabs [data-baseweb="tab-list"] {{ gap:4px; border-bottom:1px solid {T['border']}; }}
      .stTabs [data-baseweb="tab"] {{ background:transparent; border-radius:9px 9px 0 0;
          padding:8px 18px; color:{T['muted']}; font-weight:500; }}
      .stTabs [aria-selected="true"] {{ background:{T['surface_2']}; color:{T['text']};
          border:1px solid {T['border']}; border-bottom:none; }}

      .stDataFrame {{ border:1px solid {T['border']}; border-radius:10px; }}
      hr {{ border-color:{T['border']}; }}
      code, pre, .stCode {{ font-family:'JetBrains Mono',monospace !important; }}
    </style>
    """, unsafe_allow_html=True)


def card(icon: str, title: str, body: str) -> str:
    return (f"<div class='aw-card'><div class='aw-ico'>{icon}</div>"
            f"<div class='aw-body'><h4>{title}</h4><p>{body}</p></div></div>")


def header(title: str, subtitle: str = "") -> None:
    st.markdown(f"<div class='aw-wordmark'>{title}</div>", unsafe_allow_html=True)
    if subtitle:
        st.markdown(f"<div class='aw-sub'>{subtitle}</div>", unsafe_allow_html=True)
