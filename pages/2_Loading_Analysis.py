import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. 語言配置字典 ---
PAGE_LANG = {
    "繁體中文": {
        "page_title": "人力配置合理性分析",
        "sidebar_header": "⚙️ 人員名單維護",
        "pm_list": "🆔 PM 名單",
        "staff_list": "🛠️ Staff 名單",
        "btn_save_list": "💾 儲存名單變更",
        "msg_save_list": "名單同步成功！",
        "main_title": "👥 人力配置合理性分析",
        "warn_no_master": "⚠️ 請先確保主數據中有案件名稱與複雜度資訊。",
        "tabs": ["🎯 1. 案件指派", "✏️ 2. 分工比例填報", "📈 3. 負荷診斷報表"],
        "assign_header": "📝 案件團隊配置",
        "sel_proj": "📌 選擇專案",
        "sel_pm": "🆔 指派 PM",
        "sel_staff": "🛠️ 指派 Staff",
        "btn_assign": "🚀 儲存指派更新",
        "assign_msg": "指派成功！",
        "assign_overview": "📋 案件指派現況總覽表",
        "dist_missing": "目前共有 {} 個案件尚未完成分工比例填報（或占比未達 100%）：",
        "dist_success": "✅ 所有已指派 Staff 的案件皆已完成比例填報！",
        "dist_header": "✏️ 錄入具體分工占比 (%)",
        "dist_info": "請先到『案件指派』分頁完成 Staff 指派。",
        "dist_total": "📊 當前總計：**{:.1f}%**",
        "btn_save_dist": "💾 儲存分工占比",
        "report_logic_title": "⚖️ 負荷計算邏輯說明",
        "report_logic_text": "**1. Staff 總加權負荷** = Σ (案件複雜度 × 個人占比 %)  \n**2. PM 總加權複雜度** = Σ (所屬案件之複雜度總和)  \n**3. PM 平均複雜度 (核心指標)** = 總加權複雜度 / 案件總數",
        "pm_diag_title": "🆔 PM 案件負擔分析總覽",
        "pm_chart_title": "PM 負荷診斷 (共 {} 位人員)",
        "pm_table_title": "📋 PM 負荷數據匯總表",
        "pm_detail_query": "🔍 查詢指定 PM 案件明細",
        "pm_detail_prefix": "📌 **{}** 目前負責的案件明細：",
        "staff_diag_title": "📊 Staff 案件負擔分析總覽",
        "staff_chart_title": "Staff 負荷診斷 (共 {} 位人員)",
        "staff_detail_title": "🔍 人員負責案件明細",
        "staff_sel_label": "請選擇人員查看明細",
        "col_name": "姓名",
        "col_role": "角色類型",
        "col_case_name": "案件名稱",
        "col_case_type": "案件類型",
        "col_complexity": "複雜度評分",
        "col_pm": "PM名單",
        "col_staff": "Staff名單",
        "col_owner": "負責人",
        "col_ratio": "占比",
        "col_weighted": "加權負荷",
        "col_avg_complex": "平均複雜度",
        "col_total_complex": "總加權複雜度",
        "col_case_count": "案件總數"
    },
    "English": {
        "page_title": "Manpower Allocation & Stress Diagnosis",
        "sidebar_header": "⚙️ Staff Roster Maintenance",
        "pm_list": "🆔 PM Roster",
        "staff_list": "🛠️ Staff Roster",
        "btn_save_list": "💾 Save Roster Changes",
        "msg_save_list": "Roster synchronized!",
        "main_title": "👥 Case Allocation & Diagnosis",
        "warn_no_master": "⚠️ Please ensure Master Data has case names and complexity scores.",
        "tabs": ["🎯 1. Assignment", "✏️ 2. Workload Split", "📈 3. Diagnosis Report"],
        "assign_header": "📝 Team Configuration",
        "sel_proj": "📌 Select Project",
        "sel_pm": "🆔 Assign PM",
        "sel_staff": "🛠️ Assign Staff",
        "btn_assign": "🚀 Save Assignment",
        "assign_msg": "Assigned successfully!",
        "assign_overview": "📋 Assignment Status Overview",
        "dist_missing": "There are {} cases pending split completion (total not 100%):",
        "dist_success": "✅ All assigned cases completed!",
        "dist_header": "✏️ Input Workload Ratio (%)",
        "dist_info": "Please complete Staff assignment in 'Assignment' tab first.",
        "dist_total": "📊 Total: **{:.1f}%**",
        "btn_save_dist": "💾 Save Workload Ratio",
        "report_logic_title": "⚖️ Workload Calculation Logic",
        "report_logic_text": "**1. Staff Total Load** = Σ (Complexity × Personal Ratio %)  \n**2. PM Total Complexity** = Σ (Complexity of all assigned projects)  \n**3. PM Avg Complexity** = Total Complexity / Total Cases",
        "pm_diag_title": "🆔 PM Case Load Analysis",
        "pm_chart_title": "PM Load Diagnosis ({} Persons)",
        "pm_table_title": "📋 PM Load Summary Table",
        "pm_detail_query": "🔍 Query PM Details",
        "pm_detail_prefix": "📌 **{}** Current Case Details:",
        "staff_diag_title": "📊 Staff Case Load Analysis",
        "staff_chart_title": "Staff Load Diagnosis ({} Persons)",
        "staff_detail_title": "🔍 Individual Case Details",
        "staff_sel_label": "Select person to view details",
        "col_name": "Name",
        "col_role": "Role Type",
        "col_case_name": "Case Name",
        "col_case_type": "Case Type",
        "col_complexity": "Complexity Score",
        "col_pm": "PM List",
        "col_staff": "Staff List",
        "col_owner": "Owner",
        "col_ratio": "Ratio",
        "col_weighted": "Weighted Load",
        "col_avg_complex": "Avg Complexity",
        "col_total_complex": "Total Weighted Complexity",
        "col_case_count": "Total Cases"
    }
}

# 取得語系
curr_lang = st.session_state.get("lang", "繁體中文")
t = PAGE_LANG[curr_lang]

# 2. 系統路徑與檔案配置 (保留原邏輯)
current_dir = os.path.dirname(os.path.abspath(__file__))
output_folder = os.path.join(os.path.dirname(current_dir), "outputs")
if not os.path.exists(output_folder): os.makedirs(output_folder)

MASTER_FILE = os.path.join(output_folder, "master_data.xlsx")
ROI_FILE = os.path.join(output_folder, "roi_data.xlsx")
STAFF_LIST_FILE = os.path.join(output_folder, "staff_list.xlsx")
DIST_FILE = os.path.join(output_folder, "workload_distribution.xlsx")

def load_and_fix_data():
    m_df = pd.read_excel(MASTER_FILE) if os.path.exists(MASTER_FILE) else pd.DataFrame()
    if not m_df.empty and '案件類型' not in m_df.columns:
        m_df['案件類型'] = "Unclassified" if curr_lang == "English" else "未分類"
        
    r_df = pd.read_excel(ROI_FILE) if os.path.exists(ROI_FILE) else pd.DataFrame()
    
    if os.path.exists(DIST_FILE):
        d_df = pd.read_excel(DIST_FILE)
        if d_df.empty or '案件名稱' not in d_df.columns:
            d_df = pd.DataFrame(columns=['案件名稱', '負責人', '占比'])
    else:
        d_df = pd.DataFrame(columns=['案件名稱', '負責人', '占比'])
    
    if os.path.exists(STAFF_LIST_FILE):
        s_list_df = pd.read_excel(STAFF_LIST_FILE)
    else:
        s_list_df = pd.DataFrame([{"角色類型": "PM", "姓名": "Barry"}, {"角色類型": "Staff", "姓名": "Ariel"}])
    
    for df in [m_df, r_df]:
        for col in ['PM名單', 'Staff名單']:
            if col in df.columns:
                df[col] = df[col].astype(str).replace(['nan', 'None', '0.0', '0', ''], "")
    
    pm_pool = s_list_df[s_list_df['角色類型'] == 'PM']['姓名'].dropna().unique().tolist()
    staff_pool = s_list_df[s_list_df['角色類型'] == 'Staff']['姓名'].dropna().unique().tolist()
        
    return m_df, r_df, d_df, pm_pool, staff_pool, s_list_df

# --- 頁面初始設定 ---
st.set_page_config(page_title=t["page_title"], layout="wide")
master_df, roi_df, dist_df, PM_POOL, STAFF_POOL, S_LIST_DF = load_and_fix_data()

def to_list(val): return [n.strip() for n in str(val).split(',')] if val and str(val) not in ["nan", ""] else []

# --- A. 側邊欄：人員名單維護 ---
with st.sidebar:
    st.header(t["sidebar_header"])
    st.subheader(t["pm_list"])
    pm_data = S_LIST_DF[S_LIST_DF['角色類型'] == 'PM'][['姓名']].reset_index(drop=True)
    edited_pms = st.data_editor(pm_data.rename(columns={"姓名": t["col_name"]}), num_rows="dynamic", use_container_width=True, key="pm_editor", hide_index=True)
    
    st.subheader(t["staff_list"])
    staff_data = S_LIST_DF[S_LIST_DF['角色類型'] == 'Staff'][['姓名']].reset_index(drop=True)
    edited_staffs = st.data_editor(staff_data.rename(columns={"姓名": t["col_name"]}), num_rows="dynamic", use_container_width=True, key="staff_editor", hide_index=True)
    
    if st.button(t["btn_save_list"], use_container_width=True):
        final_pms = edited_pms.rename(columns={t["col_name"]: "姓名"}).dropna().copy(); final_pms['角色類型'] = 'PM'
        final_sts = edited_staffs.rename(columns={t["col_name"]: "姓名"}).dropna().copy(); final_sts['角色類型'] = 'Staff'
        pd.concat([final_pms, final_sts], ignore_index=True).to_excel(STAFF_LIST_FILE, index=False)
        st.success(t["msg_save_list"]); st.rerun()

# --- B. 主要內容區 ---
st.title(t["main_title"])

if master_df.empty:
    st.warning(t["warn_no_master"])
else:
    combined_df = master_df[['案件名稱', '案件類型', '複雜度評分']].copy()
    
    if not roi_df.empty:
        # 1. 自動清洗欄位名稱，去除不可見的空格或換行
        roi_df.columns = roi_df.columns.astype(str).str.strip()
        
        # 2. 定義目標欄位
        target_cols = ['案件名稱', 'PM名單', 'Staff名單']
        
        # 3. 檢查哪些欄位是真的存在的
        existing_cols = [c for c in target_cols if c in roi_df.columns]
        
        # 4. 如果最重要的 '案件名稱' 存在，才進行合併
        if '案件名稱' in existing_cols:
            combined_df = pd.merge(combined_df, roi_df[existing_cols], on='案件名稱', how='left').fillna("")
            
            # 5. 如果缺了 PM 或 Staff 欄位，手動補齊空值，避免後續繪圖程式碼出錯
            for col in ['PM名單', 'Staff名單']:
                if col not in combined_df.columns:
                    combined_df[col] = ""
        else:
            # 如果連 '案件名稱' 都不見了，代表 Excel 結構完全不對
            st.error(f"❌ 關鍵錯誤：在 ROI 資料中找不到 '案件名稱' 欄位。目前偵測到的欄位有：{roi_df.columns.tolist()}")
            combined_df['PM名單'], combined_df['Staff名單'] = "", ""
    else:
        # 如果 roi_df 是空的，給予預設空值
        combined_df['PM名單'], combined_df['Staff名單'] = "", ""

    tab_assign, tab_dist, tab_report = st.tabs(t["tabs"])

    # 1. 案件指派
    with tab_assign:
        st.subheader(t["assign_header"])
        proj_options = combined_df.apply(lambda x: f"[{x['案件類型']}] {x['案件名稱']}", axis=1).tolist()
        proj_mapping = dict(zip(proj_options, combined_df['案件名稱']))
        sel_option = st.selectbox(t["sel_proj"], proj_options)
        target = proj_mapping[sel_option]
        
        row_data = combined_df[combined_df['案件名稱'] == target].iloc[0]
        
        c1, c2 = st.columns(2)
        with c1:
            new_pms = st.multiselect(t["sel_pm"], PM_POOL, default=[n for n in to_list(row_data['PM名單']) if n in PM_POOL])
        with c2:
            new_sts = st.multiselect(t["sel_staff"], STAFF_POOL, default=[n for n in to_list(row_data['Staff名單']) if n in STAFF_POOL])
        
        if st.button(t["btn_assign"]):
            if roi_df.empty or target not in roi_df['案件名稱'].values:
                new_row = pd.DataFrame([{'案件名稱': target, 'PM名單': ",".join(new_pms), 'Staff名單': ",".join(new_sts)}])
                roi_df = pd.concat([roi_df, new_row], ignore_index=True)
            else:
                roi_df.loc[roi_df['案件名稱'] == target, 'PM名單'] = ",".join(new_pms)
                roi_df.loc[roi_df['案件名稱'] == target, 'Staff名單'] = ",".join(new_sts)
            roi_df.to_excel(ROI_FILE, index=False); st.success(f"{target} {t['assign_msg']}"); st.rerun()

        st.divider()
        st.subheader(t["assign_overview"])
        st.dataframe(combined_df[['案件類型', '案件名稱', '複雜度評分', 'PM名單', 'Staff名單']].rename(columns={
            "案件類型": t["col_case_type"], "案件名稱": t["col_case_name"], "複雜度評分": t["col_complexity"],
            "PM名單": t["col_pm"], "Staff名單": t["col_staff"]
        }), use_container_width=True, hide_index=True)

    # 2. 分工比例填報
    with tab_dist:
        st.subheader(t["dist_header"])
        has_staff_projs = combined_df[combined_df['Staff名單'] != ""]['案件名稱'].tolist()
        filled_projs = dist_df.groupby('案件名稱')['占比'].sum()
        completed_projs = filled_projs[abs(filled_projs - 100) < 0.1].index.tolist()
        missing_projs = [p for p in has_staff_projs if p not in completed_projs]
        
        if missing_projs:
            st.error(t["dist_missing"].format(len(missing_projs)))
            st.write(", ".join(missing_projs))
        else:
            st.success(t["dist_success"])
        
        st.divider()
        st.subheader(t["dist_header"])
        sel_proj = st.selectbox(t["sel_proj"], combined_df['案件名稱'].tolist(), key="dist_sel")
        current_staff_str = roi_df.loc[roi_df['案件名稱'] == sel_proj, 'Staff名單'].values if not roi_df.empty and sel_proj in roi_df['案件名稱'].values else []
        current_staffs = to_list(current_staff_str[0]) if len(current_staff_str) > 0 else []
        
        if not current_staffs:
            st.info(t["dist_info"])
        else:
            exist_dist = dist_df[dist_df['案件名稱'] == sel_proj] if not dist_df.empty else pd.DataFrame()
            init_df = pd.DataFrame({'負責人': current_staffs})
            if not exist_dist.empty:
                init_df = pd.merge(init_df, exist_dist[['負責人', '占比']], on='負責人', how='left').fillna(0)
            else:
                init_df['占比'] = (100 / len(current_staffs))
            
            # 翻譯 Data Editor 標題
            edited_df_ui = st.data_editor(init_df.rename(columns={"負責人": t["col_owner"], "占比": t["col_ratio"]}), use_container_width=True, hide_index=True, key="dist_editor")
            total_pct = edited_df_ui[t["col_ratio"]].sum()
            st.write(t["dist_total"].format(total_pct))
            
            if st.button(t["btn_save_dist"], disabled=(abs(total_pct - 100) > 0.01)):
                temp_dist = dist_df[dist_df['案件名稱'] != sel_proj] if not dist_df.empty else pd.DataFrame(columns=['案件名稱', '負責人', '占比'])
                new_data = edited_df_ui.rename(columns={t["col_owner"]: "負責人", t["col_ratio"]: "占比"}).copy()
                new_data['案件名稱'] = sel_proj
                pd.concat([temp_dist, new_data], ignore_index=True).to_excel(DIST_FILE, index=False)
                st.success(t["assign_msg"]); st.rerun()

    # 3. 負荷診斷報表
    with tab_report:
        with st.expander(t["report_logic_title"], expanded=False):
            st.info(t["report_logic_text"])

        if not roi_df.empty:
            pm_perf = []
            for _, row in combined_df.iterrows():
                pms = to_list(row['PM名單'])
                for p in pms:
                    if p: pm_perf.append({'PM': p, '案件名稱': row['案件名稱'], '案件類型': row['案件類型'], '複雜度': row['複雜度評分']})
            
            if pm_perf:
                pm_stats_df = pd.DataFrame(pm_perf)
                pm_summary = pm_stats_df.groupby('PM').agg(count=('案件名稱', 'count'), sum=('複雜度', 'sum')).reset_index()
                pm_summary['avg'] = (pm_summary['sum'] / pm_summary['count']).round(2)
                pm_summary = pm_summary.sort_values(by='avg', ascending=False)
                
                st.subheader(t["pm_diag_title"])
                fig_pm = px.bar(
                    pm_summary.sort_values(by='avg', ascending=True), 
                    x='avg', y='PM', orientation='h',
                    color='avg', text='avg',
                    color_continuous_scale='Blues',
                    title=t["pm_chart_title"].format(len(pm_summary)),
                    labels={'avg': t['col_avg_complex']},
                    height=max(300, len(pm_summary) * 35)
                )
                st.plotly_chart(fig_pm, use_container_width=True)
                
                st.write(t["pm_table_title"])
                disp_summary = pm_summary.rename(columns={"PM": "PM", "count": t["col_case_count"], "sum": t["col_total_complex"], "avg": t["col_avg_complex"]}).reset_index(drop=True)
                disp_summary.index += 1
                st.table(disp_summary)
                
                st.divider()
                c1, c2 = st.columns([1, 3])
                with c1:
                    target_pm = st.selectbox(t["pm_detail_query"], pm_summary['PM'].unique())
                with c2:
                    st.write(t["pm_detail_prefix"].format(target_pm))
                    pm_detail = pm_stats_df[pm_stats_df['PM'] == target_pm][['案件類型', '案件名稱', '複雜度']].rename(columns={
                        "案件類型": t["col_case_type"], "案件名稱": t["col_case_name"], "複雜度": t["col_complexity"]
                    }).reset_index(drop=True)
                    pm_detail.index += 1
                    st.table(pm_detail)
            else:
                st.subheader(t["pm_diag_title"])
                st.info("No data.")

        st.divider()
        st.subheader(t["staff_diag_title"])
        if dist_df.empty:
            st.info("💡 No data.")
        else:
            analysis_df = pd.merge(dist_df, master_df[['案件名稱', '案件類型', '複雜度評分']], on='案件名稱', how='left')
            analysis_df['加權負荷'] = (analysis_df['複雜度評分'] * (analysis_df['占比'] / 100)).round(2)
            stats = analysis_df.groupby('負責人').agg(count=('案件名稱', 'count'), sum=('加權負荷', 'sum')).reset_index().round(2).sort_values(by='sum', ascending=True)

            fig = px.bar(
                stats, x='sum', y='負責人', orientation='h',
                color='sum', text='sum',
                color_continuous_scale='Reds',
                title=t["staff_chart_title"].format(len(stats)),
                labels={'sum': t['col_weighted'], '負責人': t['col_owner']},
                height=max(400, len(stats) * 25)
            )
            st.plotly_chart(fig, use_container_width=True)

            st.divider()
            st.subheader(t["staff_detail_title"])
            selected_person = st.selectbox(t["staff_sel_label"], stats['負責人'].tolist()[::-1])
            person_detail = analysis_df[analysis_df['負責人'] == selected_person][['案件類型', '案件名稱', '複雜度評分', '占比', '加權負荷']].rename(columns={
                "案件類型": t["col_case_type"], "案件名稱": t["col_case_name"], "複雜度評分": t["col_complexity"],
                "占比": t["col_ratio"], "加權負荷": t["col_weighted"]
            }).reset_index(drop=True)
            person_detail.index += 1

            st.table(person_detail)
