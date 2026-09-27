# 401(k) Reddit 趋势 Dashboard

Streamlit dashboard for Everyday Benefits: monthly topic trends from ~8,100 Reddit posts
(r/401k + r/Retirement401k), companion to the article
https://everydaybenefits.work/learn/reddit-401k-trends

## 本地运行

```bash
pip install -r requirements.txt
streamlit run app.py
```

浏览器打开 http://localhost:8501。

## 更新数据

`data/monthly_topics.csv` 由网站仓库的分析脚本生成
(`goals/everyday-benefits-website/hidden_files/reddit-401k-compare/`)。
更新后直接替换文件、重新部署即可。

CSV 列: month (YYYY-MM), topic (机器名), label (显示名), posts, month_total, share_pct。

## 部署到 Streamlit Community Cloud

1. 登录 https://share.streamlit.io (用 GitHub 账号)
2. New app → 选择本仓库、分支 main、文件 `app.py`
3. Deploy。得到公开链接后,嵌进网站:

```html
<iframe src="https://<你的app>.streamlit.app/?embed=true"
        width="100%" height="800" frameborder="0"></iframe>
```
