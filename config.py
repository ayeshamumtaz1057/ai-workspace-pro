"""Central configuration for AI Workspace Pro."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
DB_PATH = DATA_DIR / "workspace.db"
UPLOAD_DIR = DATA_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

APP_NAME = "AI Workspace Pro"
APP_TAGLINE = "All-in-One AI Assistant"

# ---- Model / API ----------------------------------------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")

# ---- Design tokens (refined grey / slate theme) ---------------------------
THEME = {
    "bg":        "#0e1013",   # near-black graphite
    "surface":   "#16191d",   # charcoal panel
    "surface_2": "#1e2227",   # raised card
    "border":    "#2c313a",   # soft grey hairline
    "text":      "#eceef1",   # off-white
    "muted":     "#9aa1ab",   # cool grey text
    "primary":   "#7c8aa0",   # steel accent
    "accent":    "#a8b3c4",   # light steel
    "pink":      "#c0c7d1",   # neutral highlight
    "green":     "#8fb99a",   # muted sage
    "amber":     "#c9b48a",   # muted sand
    "red":       "#c98a8a",   # muted clay
}

# ---- Feature registry -----------------------------------------------------
# (key, label, icon, blurb) — drives the sidebar, home cards and left rail.
FEATURES = [
    ("home",     "Home",              "🏠", "Your workspace dashboard"),
    ("data",     "AI Data Analyst",   "📊", "Upload CSV/Excel, clean, visualize and get AI insights"),
    ("pdf",      "PDF Intelligence",  "📕", "Ask questions across multiple PDFs using RAG + FAISS"),
    ("chat",     "AI Assistant",      "💬", "Chat with Gemini, with conversation memory"),
    ("automate", "Automation Center", "📤", "Generate reports, export data, and automate workflows"),
    ("settings", "Settings",          "⚙️", "Appearance, API key and data controls"),
]

HOME_CARDS = [k for k, *_ in FEATURES if k not in ("home", "settings")]

VALUE_PROPS = [
    ("💡", "AI Powered",    "Smart responses using advanced AI models"),
    ("🔒", "Secure",        "Your data is safe and 100% private"),
    ("⚡", "Fast",          "Lightning fast performance"),
    ("👥", "User Friendly", "Clean and modern interface"),
    ("🧩", "All-in-One",    "All tools in one powerful app"),
    ("📤", "Export Reports","Export results as PDF, Excel, CSV"),
]

TECH_STACK = ["Python", "Streamlit", "Google Gemini API", "Pandas", "Plotly",
              "scikit-learn", "FAISS", "SQLite"]

LANGUAGES = ["English", "Urdu", "Arabic", "Hindi", "Spanish", "French",
             "German", "Chinese", "Japanese", "Turkish", "Russian", "Portuguese"]
