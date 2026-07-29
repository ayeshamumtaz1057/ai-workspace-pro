"""Settings — appearance, API key, language and data controls."""
import streamlit as st
from core import ai, db
from config import LANGUAGES, TECH_STACK


def render():
    st.subheader("⚙️ Settings")
    st.caption("Appearance, API access, language and your stored data.")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("**Appearance**")
        dark = st.toggle("Dark mode", value=st.session_state.get("dark", True))
        size = st.selectbox("Font size", ["Small", "Medium", "Large"],
                            index=["Small", "Medium", "Large"].index(
                                st.session_state.get("font_size", "Medium")))
        lang = st.selectbox("Interface language", LANGUAGES,
                            index=LANGUAGES.index(st.session_state.get("ui_lang", "English")))
        if (dark, size, lang) != (st.session_state.get("dark"),
                                  st.session_state.get("font_size"),
                                  st.session_state.get("ui_lang")):
            st.session_state.update(dark=dark, font_size=size, ui_lang=lang)
            db.set_setting("dark", dark)
            db.set_setting("font_size", size)
            db.set_setting("ui_lang", lang)
            st.rerun()

    with c2:
        st.markdown("**Model access**")
        key = st.text_input("Gemini API key", type="password",
                            value=st.session_state.get("api_key", ""),
                            help="Stored only in this browser session.")
        if st.button("Save key"):
            st.session_state["api_key"] = key.strip()
            st.cache_resource.clear()
            st.success("Key saved for this session.")
        st.write("Status:", "🟢 Connected" if ai.is_ready() else "🔴 Not configured")

        st.markdown("**Model**")
        if st.button("Detect available models"):
            with st.spinner("Asking the API what your key supports…"):
                found = ai.list_models()
            if found:
                st.session_state["available_models"] = found
                st.success(f"Found {len(found)} usable models.")
            else:
                st.error("Could not list models. Check that your key is saved and valid.")

        options = st.session_state.get("available_models", [])
        if options:
            current = ai.model_name()
            idx = options.index(current) if current in options else 0
            picked = st.selectbox("Active model", options, index=idx)
            if picked != current:
                st.session_state["model"] = picked
                db.set_setting("model", picked)
                st.cache_resource.clear()
                st.success(f"Now using `{picked}`.")
        else:
            st.caption(f"Currently using `{ai.model_name()}`. "
                       "Press the button above to see what your key supports.")

    st.divider()
    st.markdown("**Your data**")
    stats = db.get_stats()
    a, b, c, d = st.columns(4)
    a.metric("Chats", stats.get("chats", 0))
    b.metric("Files analyzed", stats.get("files_analyzed", 0))
    c.metric("Reports exported", stats.get("reports_exported", 0))
    d.metric("PDFs processed", stats.get("pdfs_processed", 0))

    x, y = st.columns(2)
    if x.button("Clear chat history"):
        db.clear_history()
        st.session_state.pop("chat_msgs", None)
        st.success("Chat history cleared.")
    if y.button("Log out"):
        st.session_state.clear()
        st.rerun()

    st.divider()
    st.markdown("**Tech stack**")
    st.markdown("".join(f"<span class='aw-pill'>{t}</span>" for t in TECH_STACK),
                unsafe_allow_html=True)
