"""Thin wrapper around Google Gemini with a graceful offline fallback.

Every module calls `ask()`. If no API key is configured the app still runs and
returns a clearly-labelled placeholder so the UI is testable end to end.
"""
from __future__ import annotations
import os
import streamlit as st
from config import GEMINI_MODEL

_MISSING = ("⚠️ **No API key configured.** Add `GEMINI_API_KEY` to your `.env` "
            "file (or Settings → API key) to get real model responses.")


def api_key() -> str:
    """Session override → hosting secrets → local .env, in that order."""
    if st.session_state.get("api_key"):
        return st.session_state["api_key"]
    try:                                   # Streamlit Cloud / HF Spaces secrets
        if "GEMINI_API_KEY" in st.secrets:
            return str(st.secrets["GEMINI_API_KEY"])
    except Exception:                      # no secrets.toml present locally
        pass
    return os.getenv("GEMINI_API_KEY", "")


def is_ready() -> bool:
    return bool(api_key())


def list_models() -> list[str]:
    """Ask the API which models this key can actually use for generateContent."""
    key = api_key()
    if not key:
        return []
    try:
        import google.generativeai as genai
        genai.configure(api_key=key)
        names = []
        for m in genai.list_models():
            if "generateContent" in getattr(m, "supported_generation_methods", []):
                names.append(m.name.replace("models/", ""))
        return sorted(names)
    except Exception:
        return []


def model_name() -> str:
    return st.session_state.get("model") or GEMINI_MODEL


@st.cache_resource(show_spinner=False)
def _client(key: str, model_name: str):
    import google.generativeai as genai
    genai.configure(api_key=key)
    return genai.GenerativeModel(model_name)


def ask(prompt: str, system: str = "", temperature: float = 0.7,
        history: list[dict] | None = None) -> str:
    """Send a prompt to Gemini and return plain text."""
    key = api_key()
    if not key:
        return _MISSING

    parts = []
    if system:
        parts.append(f"System instructions:\n{system}\n")
    for turn in (history or [])[-8:]:
        parts.append(f"{turn['role'].title()}: {turn['content']}")
    parts.append(f"User: {prompt}")

    try:
        model = _client(key, model_name())
        resp = model.generate_content(
            "\n\n".join(parts),
            generation_config={"temperature": temperature, "max_output_tokens": 2048},
        )
        return (resp.text or "").strip() or "The model returned an empty response. Try rephrasing."
    except Exception as exc:  # network, quota, bad key
        msg = str(exc)
        if "404" in msg or "not found" in msg or "no longer available" in msg:
            return ("❌ **That model isn't available on your key.** Open **Settings** and press "
                    "**Detect available models**, then pick one from the list.\n\n"
                    f"Details: `{msg[:300]}`")
        return f"❌ Request failed: `{msg}`\n\nCheck your API key and network, then try again."


def ask_json(prompt: str, system: str = "") -> str:
    """Ask for strict JSON (used by roadmap / planner / resume scoring)."""
    guard = ("Respond with valid JSON only. No markdown fences, no commentary.\n" + system)
    raw = ask(prompt, system=guard, temperature=0.3)
    return raw.replace("```json", "").replace("```", "").strip()
