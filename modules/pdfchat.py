"""PDF Chat — retrieval-augmented Q&A over uploaded PDFs.

Uses FAISS when available, otherwise falls back to scikit-learn TF-IDF
cosine similarity so the module always works.
"""
import numpy as np
import streamlit as st
from core import ai, db


def read_pdf(file) -> str:
    from pypdf import PdfReader
    return "\n".join((p.extract_text() or "") for p in PdfReader(file).pages)


def chunk(text: str, size: int = 900, overlap: int = 150) -> list[str]:
    words, out, i = text.split(), [], 0
    step = max(1, size - overlap)
    while i < len(words):
        out.append(" ".join(words[i:i + size]))
        i += step
    return [c for c in out if c.strip()]


class Index:
    """TF-IDF vectors, searched with FAISS if installed."""

    def __init__(self, chunks: list[str]):
        from sklearn.feature_extraction.text import TfidfVectorizer
        self.chunks = chunks
        self.vec = TfidfVectorizer(stop_words="english", max_features=8192)
        mat = self.vec.fit_transform(chunks).toarray().astype("float32")
        mat /= (np.linalg.norm(mat, axis=1, keepdims=True) + 1e-9)
        self.mat = mat
        self.faiss_index = None
        try:
            import faiss
            self.faiss_index = faiss.IndexFlatIP(mat.shape[1])
            self.faiss_index.add(mat)
        except Exception:
            pass

    def search(self, query: str, k: int = 4) -> list[str]:
        q = self.vec.transform([query]).toarray().astype("float32")
        q /= (np.linalg.norm(q) + 1e-9)
        if self.faiss_index is not None:
            _, idx = self.faiss_index.search(q, min(k, len(self.chunks)))
            order = idx[0]
        else:
            order = np.argsort(-(self.mat @ q[0]))[:k]
        return [self.chunks[i] for i in order if i >= 0]


def render():
    st.subheader("📕 PDF Chat")
    st.caption("Upload a PDF and ask questions about it.")

    files = st.file_uploader("Upload PDF(s)", type=["pdf"], accept_multiple_files=True)
    if files:
        key = tuple(f.name for f in files)
        if st.session_state.get("pdf_key") != key:
            with st.spinner("Reading and indexing…"):
                text = "\n\n".join(read_pdf(f) for f in files)
                chunks = chunk(text)
                if not chunks:
                    st.error("No selectable text found. Use the OCR tool for scanned PDFs.")
                    return
                st.session_state["pdf_index"] = Index(chunks)
                st.session_state["pdf_text"] = text
                st.session_state["pdf_key"] = key
                st.session_state["pdf_msgs"] = []
                db.bump("pdfs_processed", len(files))
            st.success(f"Indexed {len(chunks)} chunks from {len(files)} file(s).")

    if "pdf_index" not in st.session_state:
        st.info("Upload a PDF to start asking questions.")
        return

    c1, c2 = st.columns(2)
    if c1.button("Summarize the document"):
        st.session_state["pdf_pending"] = "Summarize this document in 10 bullet points."
    if c2.button("List key takeaways"):
        st.session_state["pdf_pending"] = "What are the most important takeaways and why?"

    for m in st.session_state.get("pdf_msgs", []):
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    q = st.chat_input("Ask a question about the PDF…") or st.session_state.pop("pdf_pending", None)
    if not q:
        return

    with st.chat_message("user"):
        st.markdown(q)
    ctx = "\n\n---\n\n".join(st.session_state["pdf_index"].search(q, k=5))
    with st.chat_message("assistant"), st.spinner("Searching the document…"):
        ans = ai.ask(f"CONTEXT FROM DOCUMENT:\n{ctx}\n\nQUESTION: {q}",
                     system=("Answer only from the supplied context. If the answer is not "
                             "there, say so plainly. Quote short supporting phrases."))
        st.markdown(ans)
    st.session_state["pdf_msgs"] += [{"role": "user", "content": q},
                                     {"role": "assistant", "content": ans}]
    db.log_message("PDF Chat", q, "user", q)
