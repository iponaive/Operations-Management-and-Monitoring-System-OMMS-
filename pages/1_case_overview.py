import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. 語言配置字典 ---
PAGE_LANG = {
    "繁體中文": {
        "page_title": "案件複雜度總覽",
        "main_title": "📊 營運管理報表：案件複雜度總覽",
        "warn_no_data": "⚠️ 目前暫無評分數據，請先至主頁面執行『執行評分並更新排名』。",
        "expander_title": "ℹ️ 檢視案件風險層級定義基準",
        "risk_table": {
            "風險層級": ["🔴 高 (High)", "🟡 中 (Medium)", "🔵 低 (Low)"],
            "管理含義": ["高風險、高工時、高出錯成本", "穩定產出、可訓練新人", "應該標準化、外包、丟給系統"],
            "評分區間": ["27 ~", "14 ~ 26", "1 ~ 13"],
            "建議考量": ["資深人員、薪酬平衡", "-", "-"]
        },
        "metric_total": "📊 總案件數",
        "metric_avg": "📈 平均複雜度",
        "metric_high": "🚨 高風險案件",
        "chart_type_title": "📌 案件類型與風險分佈",
        "pie_type_name": "不同案件類型佔比",
        "pie_risk_name": "風險層級分佈",
        "bar_top_title": "🏆 高複雜度案件 TOP 10",
        "bar_avg_line": "平均線",
        "scatter_title": "🔍 異常案件偵測 (資源投入 vs 複雜度)",
        "scatter_x_label": "資源投入量 (個體 + 實際系統)",
        "footer_guide": "<b>💡 管理指引：</b><br>- <b>高風險案件 (27↑)：</b> 需指派資深人員 (Senior) 負責。<br>- <b>散佈圖異常值：</b> 若案件位於左上方（低資源、高複雜度），應評估資源分配合理性。",
        "risk_levels": ["高 (High Risk)", "中 (Medium Risk)", "低 (Low Risk)"]
    },
    "English": {
        "page_title": "Case Complexity Overview",
        "main_title": "📊 Management Report: Case Complexity Overview",
        "warn_no_data": "⚠️ No data available. Please run 'Run Scoring' on the Main Page first.",
        "expander_title": "ℹ️ View Risk Level Definitions",
        "risk_table": {
            "Risk Level": ["🔴 High", "🟡 Medium", "🔵 Low"],
            "Management Meaning": ["High risk/hours/cost", "Stable/Newcomer trainable", "Standardize/Outsource"],
            "Score Range": ["27 ~", "14 ~ 26", "1 ~ 13"],
            "Suggestions": ["Senior Staffing", "-", "-"]
        },
        "metric_total": "📊 Total Cases",
        "metric_avg": "📈 Avg Complexity",
        "metric_high": "🚨 High Risk Cases",
        "chart_type_title": "📌 Case Type & Risk Distribution",
        "pie_type_name": "Case Type Share",
        "pie_risk_name": "Risk Level Share",
        "bar_top_title": "🏆 Top 10 High Complexity Cases",
        "bar_avg_line": "Average",
        "scatter_title": "🔍 Anomaly Detection (Resources vs Complexity)",
        "scatter_x_label": "Resource Input (Entities + Systems)",
        "footer_guide": "<b>💡 Guidelines:</b><br>- <b>High Risk (27↑):</b> Senior staff assigned.<br>- <b>Scatter Plot:</b> Top-left outliers (low resource/high complexity) need review.",
        "risk_levels": ["High Risk", "Medium Risk", "Low Risk"]
    }
}

# 取得主頁面傳來的語系，預設繁體中文
curr_lang = st.session_state.get("lang", "繁體中文")
t = PAGE_LANG[curr_lang]

# 1. 系統配置
st.set_page_config(page_title=t["page_title"], layout="wide")

current_dir = os.path.dirname(os.path.abspath(__file__))
output_folder = os.path.join(os.path.dirname(current_dir), "outputs")
MASTER_FILE = os.path.join(output_folder, "master_data.xlsx")

def load_data():
    if os.path.exists(MASTER_FILE):
        return pd.read_excel(MASTER_FILE)
    return pd.DataFrame()

df = load_data()

# 2. 標題
st.title(t["main_title"])

if df.empty or '複雜度評分' not in df.columns:
    st.warning(t["warn_no_data"])
else:
    # --- A. 風險層級定義 ---
    with st.expander(t["expander_title"], expanded=False):
        st.table(pd.DataFrame(t["risk_table"]))

    # 資料處理
    def classify_risk(score):
        if score >= 27: return t["risk_levels"][0]
        elif score >= 14: return t["risk_levels"][1]
        else: return t["risk_levels"][2]

    df['風險層級'] = df['複雜度評分'].apply(classify_risk)
    df['個體數'] = pd.to_numeric(df['個體數'], errors='coerce').fillna(0)
    df['實際系統數'] = pd.to_numeric(df['(系統)已考量共用情況之實際系統數'], errors='coerce').fillna(df['系統數'])
    df['調整後資源總量'] = df['個體數'] + df['實際系統數']

    # --- B. 診斷指標 ---
    col1, col2, col3 = st.columns(3)
    col1.metric(t["metric_total"], len(df))
    col2.metric(t["metric_avg"], f"{df['複雜度評分'].mean():.1f}")
    col3.metric(t["metric_high"], len(df[df['風險層級'] == t["risk_levels"][0]]))

    st.divider()

    # --- C. 視覺化圖表配置 ---
    def update_fig_layout(fig, height=450):
        fig.update_layout(
            height=height,
            margin=dict(l=80, r=10, t=50, b=10), 
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            legend=dict(orientation="v", yanchor="top", y=1, xanchor="right", x=-0.05),
            title=dict(x=0.05, xanchor='left')
        )
        return fig

    # 第一排：雙圓餅圖
    st.subheader(t["chart_type_title"])
    c1, c2 = st.columns(2)
    
    with c1:
        fig_type = px.pie(df, names='案件類型', title=t["pie_type_name"], hole=0.4)
        fig_type.update_traces(textinfo='percent') 
        st.plotly_chart(update_fig_layout(fig_type), use_container_width=True)
        
    with c2:
        fig_risk = px.pie(
            df, names='風險層級', title=t["pie_risk_name"],
            color='風險層級',
            color_discrete_map={t["risk_levels"][0]: "#ef553b", t["risk_levels"][1]: "#fecb52", t["risk_levels"][2]: "#636efa"},
            hole=0.4
        )
        fig_risk.update_traces(textinfo='percent')
        st.plotly_chart(update_fig_layout(fig_risk), use_container_width=True)

    # 第二排：長條圖
    st.subheader(t["bar_top_title"])
    top_10 = df.nlargest(10, '複雜度評分')
    fig_bar = px.bar(
        top_10, x='案件名稱', y='複雜度評分', 
        color='複雜度評分', color_continuous_scale='Reds',
        text='複雜度評分'
    )
    fig_bar.add_hline(y=df['複雜度評分'].mean(), line_dash="dash", line_color="blue", annotation_text=t["bar_avg_line"])
    fig_bar.update_layout(margin=dict(l=20, r=20, t=50, b=50))
    st.plotly_chart(fig_bar, use_container_width=True)

    # 第三排：散佈圖
    st.subheader(t["scatter_title"])
    fig_scatter = px.scatter(
        df, x='調整後資源總量', y='複雜度評分',
        size='複雜度評分', color='風險層級',
        hover_name='案件名稱',
        labels={'調整後資源總量': t["scatter_x_label"]},
        color_discrete_map={t["risk_levels"][0]: "#ef553b", t["risk_levels"][1]: "#fecb52", t["risk_levels"][2]: "#636efa"}
    )
    st.plotly_chart(update_fig_layout(fig_scatter, height=500), use_container_width=True)
    
    # 底部說明
    st.markdown(f"""
    <div style="font-size:12px; color: #888; margin-top: 10px; border-top: 1px solid #eee; padding-top: 10px;">
    {t["footer_guide"]}
    </div>
    """, unsafe_allow_html=True)