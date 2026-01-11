import streamlit as st
import pandas as pd
import os

# --- 1. 語言配置字典 ---
PAGE_LANG = {
    "繁體中文": {
        "page_title": "預算及徵才規劃",
        "main_title": "💸 預算及徵才規劃",
        "warn_no_data": "⚠️ 系統偵測到數據不足。請先完成前置分析作業。",
        "logic_header": "#### 💡 管理決策評估基準 (PM vs Staff)",
        "pm_std_title": "**🆔 PM 評估基準 (管理維度)**",
        "pm_std_text": "* **核心指標**：專案平均複雜度\n* **健康標準**：單人負責案件之平均複雜度不應超過 **10 分**，且總加權不高於 **40 分**。",
        "staff_std_title": "**🛠️ Staff 評估基準 (執行維度)**",
        "staff_std_text": "* **核心指標**：加權負荷分數 (複雜度 × 占比)\n* **健康標準**：單人總加權負荷上限為 **50 分**。",
        "table_header": "📋 案件預算效率與產值總覽",
        "col_name": "案件名稱",
        "col_complexity": "複雜度評分",
        "col_price": "最終報價(萬)",
        "col_hours": "預計工時",
        "col_unit_val": "單位產值 (萬/分)",
        "diag_header": "🚩 職能徵才需求診斷結論",
        "pm_team_eval": "##### 1️⃣ PM 團隊評估",
        "staff_team_eval": "##### 2️⃣ Staff 團隊評估",
        "metric_count": "現有 / 建議人數",
        "metric_pm_load": "總加權需求",
        "metric_staff_load": "總負荷量",
        "pm_hire_msg": "🚨 **PM 結論**：缺口 {} 人，建議啟動徵才。",
        "pm_ok_msg": "✅ **PM 結論**：管理編制目前尚屬充足。",
        "staff_hire_msg": "🚨 **Staff 結論**：缺口 {} 人，執行端壓力過大。",
        "staff_ok_msg": "✅ **Staff 結論**：執行端人力配置合理。",
        "unit_score": "分"
    },
    "English": {
        "page_title": "Budget & Recruitment Planning",
        "main_title": "💸 Budget & Recruitment Planning (Functional)",
        "warn_no_data": "⚠️ Insufficient data. Please complete previous analysis first.",
        "logic_header": "#### 💡 Decision Criteria (PM vs Staff)",
        "pm_std_title": "**🆔 PM Criteria (Management)**",
        "pm_std_text": "* **Core Metric**: Avg Project Complexity\n* **Health Std**: Avg complexity < **10 pts**, Total weighted < **40 pts** per person.",
        "staff_std_title": "**🛠️ Staff Criteria (Execution)**",
        "staff_std_text": "* **Core Metric**: Weighted Load Score\n* **Health Std**: Max weighted load cap is **50 pts** per person.",
        "table_header": "📋 Budget Efficiency & Output Overview",
        "col_name": "Case Name",
        "col_complexity": "Complexity Score",
        "col_price": "Final Quote (10k)",
        "col_hours": "Est. Hours",
        "col_unit_val": "Unit Productivity (10k/pt)",
        "diag_header": "🚩 Recruitment Requirement Diagnosis",
        "pm_team_eval": "##### 1️⃣ PM Team Evaluation",
        "staff_team_eval": "##### 2️⃣ Staff Team Evaluation",
        "metric_count": "Current / Target Headcount",
        "metric_pm_load": "Total Complexity Demand",
        "metric_staff_load": "Total Workload",
        "pm_hire_msg": "🚨 **PM Conclusion**: Shortage of {} person(s). Suggest hiring.",
        "pm_ok_msg": "✅ **PM Conclusion**: Management capacity is sufficient.",
        "staff_hire_msg": "🚨 **Staff Conclusion**: Shortage of {} person(s). High pressure.",
        "staff_ok_msg": "✅ **Staff Conclusion**: Execution capacity is balanced.",
        "unit_score": "pts"
    }
}

# 取得語系
curr_lang = st.session_state.get("lang", "繁體中文")
t = PAGE_LANG[curr_lang]

# 1. 配置與資料載入
current_dir = os.path.dirname(os.path.abspath(__file__))
output_folder = os.path.join(os.path.dirname(current_dir), "outputs")
MASTER_FILE = os.path.join(output_folder, "master_data.xlsx")
ROI_FILE = os.path.join(output_folder, "roi_data.xlsx")
STAFF_LIST_FILE = os.path.join(output_folder, "staff_list.xlsx")

st.set_page_config(page_title=t["page_title"], layout="wide")

st.title(t["main_title"])

# 檢查必要檔案
if not all(os.path.exists(f) for f in [MASTER_FILE, ROI_FILE]):
    st.warning(t["warn_no_data"])
else:
    # 2. 整合數據邏輯
    m_df = pd.read_excel(MASTER_FILE)
    r_df = pd.read_excel(ROI_FILE)
    s_list_df = pd.read_excel(STAFF_LIST_FILE) if os.path.exists(STAFF_LIST_FILE) else pd.DataFrame()
    
    budget_df = pd.merge(m_df[['案件名稱', '複雜度評分']], 
                         r_df[['案件名稱', '最終報價(萬)', '預計工時']], 
                         on='案件名稱', how='left').fillna(0)
    budget_df['單位產值'] = (budget_df['最終報價(萬)'] / budget_df['複雜度評分']).replace([float('inf')], 0).fillna(0)

    # --- A. 版面優化：評估基準區塊 ---
    with st.container(border=True):
        st.markdown(t["logic_header"])
        logic_col1, logic_col2 = st.columns(2)
        
        with logic_col1:
            st.markdown(t["pm_std_title"])
            st.markdown(t["pm_std_text"])
            
        with logic_col2:
            st.markdown(t["staff_std_title"])
            st.markdown(t["staff_std_text"])

    st.write("") 

    # 3. 案件預算效率與產值總覽
    st.subheader(t["table_header"])
    st.dataframe(
        budget_df[['案件名稱', '複雜度評分', '最終報價(萬)', '預計工時', '單位產值']].rename(columns={
            "案件名稱": t["col_name"], "複雜度評分": t["col_complexity"],
            "最終報價(萬)": t["col_price"], "預計工時": t["col_hours"], "單位產值": t["col_unit_val"]
        }),
        column_config={
            t["col_unit_val"]: st.column_config.NumberColumn(t["col_unit_val"], format="%.2f"),
            t["col_price"]: st.column_config.NumberColumn(t["col_price"]),
        },
        hide_index=True, 
        use_container_width=True 
    )

    st.divider()

    # --- B. 職能需求結論 ---
    st.subheader(t["diag_header"])
    
    if not s_list_df.empty:
        curr_pm_cnt = len(s_list_df[s_list_df['角色類型'] == 'PM'])
        curr_staff_cnt = len(s_list_df[s_list_df['角色類型'] == 'Staff'])
    else:
        curr_pm_cnt, curr_staff_cnt = 5, 2

    total_load = budget_df['複雜度評分'].sum()
    req_pm = round(total_load / 40.0, 1)
    req_staff = round(total_load / 50.0, 1)

    result_pm_col, result_staff_col = st.columns(2)

    with result_pm_col:
        st.markdown(t["pm_team_eval"])
        m1, m2 = st.columns(2)
        m1.metric(t["metric_count"], f"{curr_pm_cnt} / {req_pm}")
        m2.metric(t["metric_pm_load"], f"{total_load} {t['unit_score']}")
        
        if req_pm > curr_pm_cnt:
            st.error(t["pm_hire_msg"].format(round(req_pm - curr_pm_cnt, 1)))
        else:
            st.success(t["pm_ok_msg"])

    with result_staff_col:
        st.markdown(t["staff_team_eval"])
        s1, s2 = st.columns(2)
        s1.metric(t["metric_count"], f"{curr_staff_cnt} / {req_staff}")
        s2.metric(t["metric_staff_load"], f"{total_load} {t['unit_score']}")
        
        if req_staff > curr_staff_cnt:
            st.error(t["staff_hire_msg"].format(round(req_staff - curr_staff_cnt, 1)))
        else:
            st.success(t["staff_ok_msg"])