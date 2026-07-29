"""AI Chat — general purpose conversational assistant."""
import streamlit as st
from core import ai, db

SYSTEM = ("You are AI Workspace Pro's assistant. Answer clearly and concisely, "
          "use markdown, and prefer short paragraphs and bullet lists.")

PRESETS = ["Explain the difference between AI, ML, DL and NLP",
           "Summarise this text in five bullets",
           "Interview questions for a data analyst role"]


def render():
    st.subheader("💬 AI Chat")
    st.caption("Chat with AI and get intelligent answers to any question.")

    st.session_state.setdefault("chat_msgs", [])
    cols = st.columns(len(PRESETS))
    for i, (col, preset) in enumerate(zip(cols, PRESETS)):
        if col.button(preset, key=f"preset_{i}", use_container_width=True):
            st.session_state["chat_pending"] = preset

    for m in st.session_state["chat_msgs"]:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    prompt = st.chat_input("Type your message…") or st.session_state.pop("chat_pending", None)
    if not prompt:
        return

    st.session_state["chat_msgs"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"), st.spinner("Thinking…"):
        reply = ai.ask(prompt, system=SYSTEM, history=st.session_state["chat_msgs"][:-1])
        st.markdown(reply)

    st.session_state["chat_msgs"].append({"role": "assistant", "content": reply})
    db.log_message("AI Chat", prompt, "user", prompt)
    db.log_message("AI Chat", prompt, "assistant", reply)
    db.bump("chats")
