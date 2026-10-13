import streamlit as st
import akshare as ak
import plotly.express as px
import pandas as pd
import numpy as np

# -------------------------- 页面基础配置 --------------------------
st.set_page_config(layout="wide", page_title="多标的股票监控工作台")
st.title("📊 多股票并行监控工作台（10标的）")
st.caption("学术项目｜仅行情可视化监控，不提供自动交易功能")

# -------------------------- 【在这里修改你要监控的10只股票】 --------------------------
# 格式："股票代码":"股票名字"
watch_list = {
    "600036": "招商银行",
    "600519": "贵州茅台",
    "000001": "平安银行",
    "002594": "比亚迪",
    "601318": "中国平安",
    "000858": "五粮液",
    "600989": "宝丰能源",
    "002714": "牧原股份",
    "601899": "紫金矿业",
    "300750": "宁德时代"
}
stock_codes = list(watch_list.keys())

# -------------------------- 侧边栏参数设置 --------------------------
with st.sidebar:
    st.header("⚙️ 参数控制面板")
    period = st.radio("行情周期", ["日线", "周线"], horizontal=True)
    alert_threshold = st.slider("振幅告警阈值 %", min_value=1.0, max_value=10.0, value=3.0, step=0.2)
    fetch_count = st.slider("获取最近多少根K线", min_value=20, max_value=120, value=60)
    refresh_btn = st.button("🔄 刷新全部行情")

# -------------------------- 行情获取函数 --------------------------
@st.cache_data(ttl=300)
def get_stock_data(code, period_type, count):
    if period_type == "日线":
        df = ak.stock_zh_a_hist(symbol=code, period="daily", adjust="qfq")
    else:
        df = ak.stock_zh_a_hist(symbol=code, period="weekly", adjust="qfq")
    df = df.tail(count)
    df = df.reset_index(drop=True)
    return df

# -------------------------- 循环渲染每一行标的 --------------------------
st.subheader("标的监控列表")
for code in stock_codes:
    stock_name = watch_list[code]
    try:
        df = get_stock_data(code, period, fetch_count)
        last_price = df["收盘"].iloc[-1]
        first_price = df["收盘"].iloc[0]
        change_pct = (last_price - first_price) / first_price * 100
        high = df["最高"].max()
        low = df["最低"].min()
        amplitude = (high - low) / low * 100

        # 判断告警状态
        if amplitude >= alert_threshold:
            status_text = "⚠️ 异动预警"
            bg_color = "#fff2cc"
        else:
            status_text = "✅ 正常"
            bg_color = "#f0f8f0"

        # 生成迷你价格曲线
        fig = px.line(df, y="收盘", height=80, width=240)
        fig.update_layout(
            margin=dict(l=0, r=0, t=0, b=0),
            xaxis_visible=False,
            yaxis_visible=False,
            showlegend=False
        )

        # 一行5列布局
        with st.container(border=True):
            col1, col2, col3, col4, col5 = st.columns([1, 1, 3, 1, 1])
            with col1:
                st.write(f"**{stock_name}**\n`{code}`")
            with col2:
                st.write(f"现价：{last_price:.2f}")
            with col3:
                st.plotly_chart(fig, config={"displayModeBar": False})
            with col4:
                st.write(f"区间涨跌：{change_pct:.2f}%")
            with col5:
                st.markdown(f":{bg_color}[{status_text}]\n振幅:{amplitude:.2f}%")

    except Exception as e:
        st.error(f"获取 {code} {stock_name} 行情失败: {str(e)}")

st.divider()
st.info("💡 使用说明：当标的区间振幅超过阈值，整行标记黄色预警，优先关注预警标的，降低同时监控10只股票的工作量。")
