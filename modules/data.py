"""Data Analysis — upload CSV/Excel, profile, chart with Plotly, AI insights."""
import io
import pandas as pd
import plotly.express as px
import streamlit as st
from core import ai, db

DEMO = pd.DataFrame({
    "Date": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"],
    "Product": ["Laptop", "Chair", "Phone", "Table"],
    "Category": ["Electronics", "Furniture", "Electronics", "Furniture"],
    "Sales": [1200, 150, 800, 300],
})


def _load(file):
    if file is None:
        return DEMO.copy()
    if file.name.lower().endswith((".xlsx", ".xls")):
        return pd.read_excel(file)
    return pd.read_csv(file)


def render():
    st.subheader("📊 Data Analysis")
    st.caption("Upload your data, clean it, visualize and get AI insights.")

    file = st.file_uploader("Upload CSV / Excel file", type=["csv", "xlsx", "xls"])
    try:
        df = _load(file)
    except Exception as exc:
        st.error(f"Could not read that file: {exc}")
        return
    if file:
        db.bump("files_analyzed")

    tabs = st.tabs(["Preview", "Clean", "Visualize", "AI Insights", "Export"])

    with tabs[0]:
        st.dataframe(df.head(50), use_container_width=True)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Rows", len(df))
        c2.metric("Columns", df.shape[1])
        c3.metric("Missing values", int(df.isna().sum().sum()))
        c4.metric("Duplicates", int(df.duplicated().sum()))
        st.write("**Column summary**")
        st.dataframe(df.describe(include="all").T, use_container_width=True)

    with tabs[1]:
        c1, c2 = st.columns(2)
        drop_dupes = c1.checkbox("Drop duplicate rows")
        fill = c2.selectbox("Fill missing values with",
                            ["Leave as is", "0", "Mean (numeric)", "Median (numeric)", "Drop rows"])
        clean = df.copy()
        if drop_dupes:
            clean = clean.drop_duplicates()
        num = clean.select_dtypes("number").columns
        if fill == "0":
            clean = clean.fillna(0)
        elif fill == "Mean (numeric)":
            clean[num] = clean[num].fillna(clean[num].mean())
        elif fill == "Median (numeric)":
            clean[num] = clean[num].fillna(clean[num].median())
        elif fill == "Drop rows":
            clean = clean.dropna()
        st.dataframe(clean.head(50), use_container_width=True)
        st.session_state["clean_df"] = clean

    with tabs[2]:
        work = st.session_state.get("clean_df", df)
        kind = st.selectbox("Chart type", ["Bar", "Line", "Pie", "Scatter", "Histogram", "Box"])
        cols = list(work.columns)
        c1, c2 = st.columns(2)
        x = c1.selectbox("X / labels", cols)
        y = c2.selectbox("Y / values", cols, index=min(len(cols) - 1, 3))
        try:
            if kind == "Bar":
                fig = px.bar(work, x=x, y=y, color=x)
            elif kind == "Line":
                fig = px.line(work, x=x, y=y, markers=True)
            elif kind == "Pie":
                fig = px.pie(work, names=x, values=y, hole=.45)
            elif kind == "Scatter":
                fig = px.scatter(work, x=x, y=y, color=x, size_max=18)
            elif kind == "Histogram":
                fig = px.histogram(work, x=x)
            else:
                fig = px.box(work, x=x, y=y)
            fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
                              plot_bgcolor="rgba(0,0,0,0)", height=420)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as exc:
            st.warning(f"That column pairing doesn't work for a {kind.lower()} chart: {exc}")

    with tabs[3]:
        if st.button("Analyze with AI", type="primary"):
            work = st.session_state.get("clean_df", df)
            profile = (f"Shape: {work.shape}\nColumns: {list(work.columns)}\n"
                       f"Types:\n{work.dtypes.to_string()}\n\n"
                       f"Head:\n{work.head(15).to_string()}\n\n"
                       f"Describe:\n{work.describe(include='all').T.to_string()}")
            with st.spinner("Reading your dataset…"):
                out = ai.ask(profile,
                             system=("You are a data analyst. Give: 1) what this dataset is, "
                                     "2) five concrete insights with numbers, 3) data quality "
                                     "issues, 4) three recommended next analyses. Use markdown."))
            st.markdown(out)
            db.log_message("Data Analysis", file.name if file else "sample.csv", "user", "analyze")

    with tabs[4]:
        work = st.session_state.get("clean_df", df)
        st.download_button("Download CSV", work.to_csv(index=False).encode(),
                           "analysis.csv", "text/csv")
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as xl:
            work.to_excel(xl, index=False, sheet_name="Data")
        st.download_button("Download Excel", buf.getvalue(), "analysis.xlsx")
