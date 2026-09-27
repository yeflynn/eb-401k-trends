"""Everyday Benefits — 401(k) Reddit 趋势 Dashboard.

数据源: r/401k + r/Retirement401k 约 8,100 帖,按关键词 first-match 粗分类,
按月聚合。详细方法见页面底部的说明。
"""
import pandas as pd
import streamlit as st

# ---------- 页面配置 ----------
st.set_page_config(
    page_title="401(k) Reddit 趋势 | Everyday Benefits",
    page_icon="📊",
    layout="wide",
)

# ---------- 读数据 ----------
# @st.cache_data: 数据只读一次并缓存,之后每次互动(点选框/滑杆)重跑脚本时
# 不会重复读文件。这是 Streamlit 最核心的性能机制:脚本每次互动都会从头重跑。
@st.cache_data
def load_data():
    df = pd.read_csv("data/monthly_topics.csv", parse_dates=["month"])
    return df

df = load_data()

# ---------- 标题区 ----------
st.title("What are people asking about their 401(k)?")
st.markdown(
    "基于约 **8,100** 条 Reddit 帖子 (r/401k + r/Retirement401k, 2024-09 → 2026-09) "
    "的话题趋势。数据每月更新。\n\n"
    "📖 完整分析文章: [What 8,000 Reddit Posts Tell Us About America's 401(k) Questions]"
    "(https://everydaybenefits.work/learn/reddit-401k-trends)"
)

# 年度划分(与文章一致,按整月近似)
df["period"] = df["month"].apply(
    lambda m: "Year 1 (2024-09–2025-08)"
    if m < pd.Timestamp("2025-09-01")
    else "Year 2 (2025-09–2026-09)"
)

# ---------- 侧边栏:筛选器 ----------
# Streamlit 的交互逻辑:每个 widget (multiselect/radio/slider) 都是一个变量,
# 用户一改,整个脚本从上到下重跑一遍,用新值重新渲染。不需要写回调函数。
st.sidebar.header("筛选")
all_topics = sorted(df["label"].unique())

# 默认选中总量最大的 5 个话题,避免 16 条线糊在一起
top5 = (
    df.groupby("label")["posts"].sum().sort_values(ascending=False).head(5).index.tolist()
)
topics = st.sidebar.multiselect("话题", all_topics, default=top5)

metric = st.sidebar.radio("指标", ["占比 %", "帖子数"], index=0)

months = sorted(df["month"].unique())
date_range = st.sidebar.slider(
    "月份范围",
    min_value=months[0].date(),
    max_value=months[-1].date(),
    value=(months[0].date(), months[-1].date()),
    format="YYYY-MM",
)

if not topics:
    st.warning("请至少选择一个话题。")
    st.stop()

# ---------- 过滤 ----------
mask = (
    df["label"].isin(topics)
    & (df["month"] >= pd.Timestamp(date_range[0]))
    & (df["month"] <= pd.Timestamp(date_range[1]))
)
fdf = df[mask].copy()
value_col = "share_pct" if metric == "占比 %" else "posts"

# ---------- 图 1:月度趋势 ----------
st.subheader(f"月度趋势 — {metric}")
pivot = fdf.pivot_table(index="month", columns="label", values=value_col, aggfunc="sum")
st.line_chart(pivot, height=380)

# ---------- 图 2:年度对比 ----------
yoy_title = "年度对比 — 各话题占比变化" if metric == "占比 %" else "年度对比 — 各话题帖子数"
st.subheader(yoy_title)
yoy = (
    fdf.groupby(["period", "label"])[value_col].mean().reset_index()
    if metric == "占比 %"
    else fdf.groupby(["period", "label"])["posts"].sum().reset_index()
)
yoy_pivot = yoy.pivot(index="label", columns="period", values=value_col)
st.bar_chart(yoy_pivot, height=380)

# ---------- 数据表 ----------
with st.expander("查看原始数据"):
    show = fdf[["month", "label", "posts", "month_total", "share_pct"]].sort_values(
        ["month", "posts"], ascending=[True, False]
    )
    show["month"] = show["month"].dt.strftime("%Y-%m")
    st.dataframe(show, use_container_width=True, hide_index=True)
    csv = show.to_csv(index=False).encode("utf-8")
    st.download_button("下载 CSV", csv, "monthly_401k_topics.csv", "text/csv")

# ---------- 方法说明 ----------
with st.expander("方法与注意事项"):
    st.markdown(
        """
- **分类方法**: 关键词 first-match 粗分类,同一套规则应用于两个年度,相对变化有意义,
  但绝对数字不能当作严格研究结论。
- **数据缺口**: r/401k 在 2025 年年中之前有明显存档缺口,2025 年年中之前的月份
  主要由 r/Retirement401k 驱动,帖子量偏少。
- **更新频率**: 月度批次更新,非实时。
- Educational content only — not financial or tax advice.
"""
    )

st.caption("Everyday Benefits · https://everydaybenefits.work")
