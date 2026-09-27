"""Everyday Benefits — 401(k) Reddit trends dashboard.

Data: ~8,100 posts from r/401k + r/Retirement401k, grouped by keyword
first-match classification, aggregated monthly. See the method note
at the bottom of the page for details.
"""
import pandas as pd
import streamlit as st

# ---------- Page config ----------
st.set_page_config(
    page_title="401(k) Reddit Trends | Everyday Benefits",
    page_icon="📊",
    layout="wide",
)

# ---------- Load data ----------
# @st.cache_data: the CSV is read once and cached. Every widget interaction
# re-runs the whole script top to bottom, but cached results are reused
# instead of re-reading the file. This is Streamlit's core performance trick.
@st.cache_data
def load_data():
    df = pd.read_csv("data/monthly_topics.csv", parse_dates=["month"])
    return df

df = load_data()

# ---------- Header ----------
st.title("What are people asking about their 401(k)?")
st.markdown(
    "Topic trends from about **8,100** Reddit posts "
    "(r/401k + r/Retirement401k, Sep 2024 → Sep 2026). Updated monthly.\n\n"
    "📖 Full analysis: [What 8,000 Reddit Posts Tell Us About America's 401(k) Questions]"
    "(https://everydaybenefits.work/learn/reddit-401k-trends)"
)

# Year split (matches the article, approximated to whole months)
df["period"] = df["month"].apply(
    lambda m: "Year 1 (Sep 2024–Aug 2025)"
    if m < pd.Timestamp("2025-09-01")
    else "Year 2 (Sep 2025–Sep 2026)"
)

# ---------- Sidebar: filters ----------
# How Streamlit interaction works: each widget (multiselect/radio/slider)
# is just a variable. When the user changes one, the entire script re-runs
# from top to bottom with the new values and re-renders. No callbacks needed.
st.sidebar.header("Filters")
all_topics = sorted(df["label"].unique())

# Default to the 5 biggest topics so 16 lines don't turn into spaghetti
top5 = (
    df.groupby("label")["posts"].sum().sort_values(ascending=False).head(5).index.tolist()
)
topics = st.sidebar.multiselect("Topics", all_topics, default=top5)

metric = st.sidebar.radio("Metric", ["Share %", "Post count"], index=0)

months = sorted(df["month"].unique())
date_range = st.sidebar.slider(
    "Month range",
    min_value=months[0].date(),
    max_value=months[-1].date(),
    value=(months[0].date(), months[-1].date()),
    format="YYYY-MM",
)

if not topics:
    st.warning("Please select at least one topic.")
    st.stop()

# ---------- Filter ----------
mask = (
    df["label"].isin(topics)
    & (df["month"] >= pd.Timestamp(date_range[0]))
    & (df["month"] <= pd.Timestamp(date_range[1]))
)
fdf = df[mask].copy()
value_col = "share_pct" if metric == "Share %" else "posts"

# ---------- Chart 1: monthly trend ----------
st.subheader(f"Monthly trend — {metric}")
pivot = fdf.pivot_table(index="month", columns="label", values=value_col, aggfunc="sum")
st.line_chart(pivot, height=380)

# ---------- Chart 2: year-over-year ----------
yoy_title = (
    "Year-over-year — topic share" if metric == "Share %" else "Year-over-year — post count"
)
st.subheader(yoy_title)
yoy = (
    fdf.groupby(["period", "label"])[value_col].mean().reset_index()
    if metric == "Share %"
    else fdf.groupby(["period", "label"])["posts"].sum().reset_index()
)
yoy_pivot = yoy.pivot(index="label", columns="period", values=value_col)
st.bar_chart(yoy_pivot, height=380)

# ---------- Data table ----------
with st.expander("View raw data"):
    show = fdf[["month", "label", "posts", "month_total", "share_pct"]].sort_values(
        ["month", "posts"], ascending=[True, False]
    )
    show["month"] = show["month"].dt.strftime("%Y-%m")
    st.dataframe(show, use_container_width=True, hide_index=True)
    csv = show.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", csv, "monthly_401k_topics.csv", "text/csv")

# ---------- Method note ----------
with st.expander("Method & caveats"):
    st.markdown(
        """
- **Classification**: keyword first-match grouping. The same rules were applied
  to both years, so relative changes are meaningful — but treat absolute
  numbers as directional, not research-grade coding.
- **Data gap**: r/401k has a clear archive gap before mid-2025, so months
  before then are driven mostly by r/Retirement401k and post counts are lower.
- **Update cadence**: monthly batches, not real-time.
- Educational content only — not financial or tax advice.
"""
    )

st.caption("Everyday Benefits · https://everydaybenefits.work")
