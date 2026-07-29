"""AI Workspace Pro — All-in-One AI Assistant.

Run with:  streamlit run app.py
"""
import streamlit as st

from config import APP_NAME, APP_TAGLINE, FEATURES, VALUE_PROPS, TECH_STACK
from core import db
from core.theme import inject_css, card, header
from modules import chat, data, pdfchat, automate, settings

ROUTES = {
    "chat": chat, "data": data, "pdf": pdfchat,
    "automate": automate, "settings": settings,
}

STAT_LABELS = [("chats", "💬", "Chats"), ("files_analyzed", "📄", "Files Analyzed"),
               ("pdfs_processed", "📕", "PDFs Processed"),
               ("reports_exported", "📤", "Reports Exported")]


def boot():
    st.set_page_config(page_title=APP_NAME, page_icon="🧠", layout="wide",
                       initial_sidebar_state="expanded")
    db.init_db()
    st.session_state.setdefault("page", "home")
    st.session_state.setdefault("dark", db.get_setting("dark", "True") == "True")
    st.session_state.setdefault("font_size", db.get_setting("font_size", "Medium"))
    st.session_state.setdefault("ui_lang", db.get_setting("ui_lang", "English"))
    st.session_state.setdefault("user", "Ayesha")
    saved_model = db.get_setting("model")
    if saved_model:
        st.session_state.setdefault("model", saved_model)
    inject_css(st.session_state["font_size"], st.session_state["dark"])


def sidebar():
    with st.sidebar:
        st.markdown(f"### 🧠 {APP_NAME}")
        st.markdown("<span class='aw-muted'>PRO</span>", unsafe_allow_html=True)
        st.divider()
        for key, label, icon, _ in FEATURES:
            kind = "primary" if st.session_state["page"] == key else "secondary"
            if st.button(f"{icon}  {label}", key=f"nav_{key}",
                         use_container_width=True, type=kind):
                st.session_state["page"] = key
                st.rerun()
        st.divider()
        st.markdown("<span class='aw-muted'>Tech stack</span>", unsafe_allow_html=True)
        st.markdown("".join(f"<span class='aw-pill'>{t}</span>" for t in TECH_STACK),
                    unsafe_allow_html=True)


def home():
    header(APP_NAME.upper(), APP_TAGLINE)

    st.markdown(
        f"<div class='aw-banner'><b>Welcome back, {st.session_state['user']}! 👋</b>"
        f"<span>Your AI workspace — four tools, one clean dashboard.</span></div>",
        unsafe_allow_html=True)

    main, rail = st.columns([3, 1], gap="large")

    with main:
        cards = [f for f in FEATURES if f[0] not in ("home", "settings")]
        # two-column clean grid (portal-like), each card with an Open button
        for row_start in range(0, len(cards), 2):
            cols = st.columns(2, gap="medium")
            for col, (key, label, icon, blurb) in zip(
                    cols, cards[row_start:row_start + 2]):
                with col:
                    st.markdown(card(icon, label, blurb), unsafe_allow_html=True)
                    if st.button(f"Open  {label}", key=f"open_{key}",
                                 use_container_width=True):
                        st.session_state["page"] = key
                        st.rerun()
                    st.write("")

    with rail:
        recents = db.recent_chats(5)
        rows = "".join(
            f"<div class='aw-row'><span>{r['module']} · {r['title'][:22]}</span>"
            f"<span class='aw-muted'>{r['ts'][5:16].replace('T', ' ')}</span></div>"
            for r in recents) or "<div class='aw-muted'>Nothing yet — get started.</div>"
        st.markdown(f"<div class='aw-panel'><h3>Recent activity</h3>{rows}</div>",
                    unsafe_allow_html=True)

        st.write("")
        stats = db.get_stats()
        srows = "".join(
            f"<div class='aw-row'><span>{i} {lbl}</span><b>{stats.get(k, 0)}</b></div>"
            for k, i, lbl in STAT_LABELS)
        st.markdown(f"<div class='aw-panel'><h3>Quick stats</h3>{srows}</div>",
                    unsafe_allow_html=True)

    st.write("")
    st.markdown("---")
    for col, (icon, title, body) in zip(st.columns(6), VALUE_PROPS):
        col.markdown(f"<div class='aw-strip'>{icon} <b>{title}</b><span>{body}</span></div>",
                     unsafe_allow_html=True)


def main():
    boot()
    sidebar()
    page = st.session_state["page"]
    if page == "home":
        home()
    else:
        if st.button("← Back to dashboard"):
            st.session_state["page"] = "home"
            st.rerun()
        ROUTES[page].render()


if __name__ == "__main__":
    main()
