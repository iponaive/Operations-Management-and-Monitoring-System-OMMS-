import streamlit as st
import pandas as pd
import glob
import os
import scorer  # 確保同層級有 scorer.py 檔案

# --- 1. 定義語系對照表 ---
LANG_PACKAGE = {
    "繁體中文": {
        "page_title": "營運管理系統",
        "diag_header": "🔍 資料診斷資訊",
        "total_rows": "總筆數",
        "reset_btn": "🗑️ 重設資料 (重新匯入 Excel)",
        "no_data": "目前暫無資料",
        "main_title": "⚖️ 案件主檔明細",
        "tab_edit": "📝 輸入案件資訊",
        "tab_rank": "🏆 複雜度評分結果",
        "edit_subheader": "主資料編輯區",
        "info_msg": "請將檔案放入 `inputs_raw_cases` 後按重新整理。",
        "col_seq": "序號",
        "col_entities": "個體數",
        "col_systems": "系統數",
        "btn_run": "🚀 執行評分並更新排名",
        "btn_save": "💾 僅儲存編輯內容",
        "msg_score_done": "評分已完成！各分頁報表已同步更新。",
        "msg_save_done": "編輯內容已儲存！",
        "rank_subheader": "案件複雜度排名預覽",
        "col_rank": "排名",
        "col_score": "複雜度評分",
        "btn_download": "📥 下載完整評分報表 (CSV)",
        "warn_no_score": "⚠️ 尚未產生評分，請至編輯區執行評分。"
    },
    "English": {
        "page_title": "Operation Management System",
        "diag_header": "🔍 Data Diagnostics",
        "total_rows": "Total Records",
        "reset_btn": "🗑️ Reset Data (Re-import Excel)",
        "no_data": "No Data Available",
        "main_title": "⚖️ Case Master Details",
        "tab_edit": "📝 Input Case Information",
        "tab_rank": "🏆 Complexity Results",
        "edit_subheader": "Master Data Editor",
        "info_msg": "Please place files in `inputs_raw_cases` and refresh.",
        "col_seq": "Seq",
        "col_entities": "Entities",
        "col_systems": "Systems",
        "btn_run": "🚀 Run Scoring & Update Rank",
        "btn_save": "💾 Save Changes Only",
        "msg_score_done": "Scoring completed! All reports synchronized.",
        "msg_save_done": "Changes saved successfully!",
        "rank_subheader": "Complexity Ranking Preview",
        "col_rank": "Rank",
        "col_score": "Complexity Score",
        "btn_download": "📥 Download Full Report (CSV)",
        "warn_no_score": "⚠️ No scores generated. Please run scoring in the editor."
    }
}

# --- 2. 修正核心報錯：優先執行 Page Config ---
# 為避免 StreamlitSetPageConfigMustBeFirstCommandError
# 我們先暫時設定一個固定的 Title，或從 Session State 抓取
st.set_page_config(page_title="營運管理系統", layout="wide")

# --- 3. 系統路徑與配置 ---
current_dir = os.path.dirname(os.path.abspath(__file__))
target_folder = os.path.join(current_dir, "inputs_raw_cases")
output_folder = os.path.join(current_dir, "outputs")
MASTER_FILE = os.path.join(output_folder, "master_data.xlsx")
os.makedirs(output_folder, exist_ok=True)

# 語系選擇器
if 'lang' not in st.session_state:
    st.session_state.lang = "繁體中文"

with st.sidebar:
    st.session_state.lang = st.selectbox("🌐 Language / 語系", ["繁體中文", "English"])
    
t = LANG_PACKAGE[st.session_state.lang]

# --- 4. 資料初始化邏輯 (完全保留) ---
def load_initial_data():
    if os.path.exists(MASTER_FILE):
        return pd.read_excel(MASTER_FILE)
    
    files = glob.glob(os.path.join(target_folder, "*.xls*"))
    all_data = []
    for f in files:
        if os.path.basename(f).startswith("~$"): continue
        temp_df = pd.read_excel(f, header=0)
        temp_df.columns = temp_df.columns.str.strip() 
        all_data.append(temp_df)
    
    if all_data:
        df_raw = pd.concat(all_data, ignore_index=True).dropna(how='all')
        df_raw.to_excel(MASTER_FILE, index=False)
        return df_raw
    return pd.DataFrame()

if 'df' not in st.session_state:
    st.session_state.df = load_initial_data()

# --- 5. 側邊欄：診斷資訊 ---
with st.sidebar:
    st.header(t["diag_header"])
    if not st.session_state.df.empty:
        st.write(f"**{t['total_rows']}:** {len(st.session_state.df)}")
        
        null_series = st.session_state.df.isnull().sum()
        null_df = null_series[null_series > 0].reset_index()
        if not null_df.empty:
            null_df.columns = ['欄位名稱', '空格數量']
            null_df.insert(0, t["col_seq"], range(1, len(null_df) + 1))
            st.dataframe(null_df, hide_index=True, use_container_width=True)
        
        st.divider()
        if st.button(t["reset_btn"], use_container_width=True):
            if os.path.exists(MASTER_FILE): os.remove(MASTER_FILE)
            st.session_state.df = pd.DataFrame()
            st.rerun()
    else:
        st.warning(t["no_data"])

# --- 6. 主要工作區 ---
st.title(t["main_title"])
tab1, tab2 = st.tabs([t["tab_edit"], t["tab_rank"]])

with tab1:
    st.subheader(t["edit_subheader"])
    if st.session_state.df.empty:
        st.info(t["info_msg"])
    else:
        df_for_edit = st.session_state.df.copy()
        if '複雜度評分' in df_for_edit.columns:
            df_for_edit = df_for_edit.drop(columns=['複雜度評分'])
        if '序號' in df_for_edit.columns:
            df_for_edit = df_for_edit.drop(columns=['序號'])
        df_for_edit.insert(0, '序號', range(1, len(df_for_edit) + 1))
        
        # 顯示時翻譯標題
        edited_df_raw = st.data_editor(
            df_for_edit.rename(columns={"序號": t["col_seq"], "個體數": t["col_entities"], "系統數": t["col_systems"]}), 
            num_rows="dynamic", 
            use_container_width=True,
            hide_index=True,
            column_config={
                t["col_seq"]: st.column_config.NumberColumn(t["col_seq"], disabled=True),
            },
            key="data_editor_main"
        )
        
        # 反向還原中文 Key 以利 scorer 運算
        reverse_map = {t["col_seq"]: "序號", t["col_entities"]: "個體數", t["col_systems"]: "系統數"}
        temp_edited = edited_df_raw.rename(columns=reverse_map)
        temp_edited = temp_edited.drop(columns=['序號']) if '序號' in temp_edited.columns else temp_edited
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button(t["btn_run"], use_container_width=True):
                clean_data = temp_edited.copy()
                num_cols = clean_data.select_dtypes(include=['number']).columns
                clean_data[num_cols] = clean_data[num_cols].fillna(0)
                obj_cols = clean_data.select_dtypes(include=['object', 'string']).columns
                clean_data[obj_cols] = clean_data[obj_cols].fillna("")
                clean_data = clean_data.reset_index(drop=True)
                df_ranked = scorer.calculate_complexity(clean_data)
                
                if '序號' in df_ranked.columns:
                    df_ranked = df_ranked.drop(columns=['序號'])
                df_ranked.insert(0, '序號', range(1, len(df_ranked) + 1))
                st.session_state.df = df_ranked
                df_ranked.to_excel(MASTER_FILE, index=False)
                st.success(t["msg_score_done"])
                st.rerun()
                
        with col2:
            if st.button(t["btn_save"], use_container_width=True):
                save_data = temp_edited.copy()
                save_data.insert(0, '序號', range(1, len(save_data) + 1))
                st.session_state.df = save_data
                save_data.to_excel(MASTER_FILE, index=False)
                st.success(t["msg_save_done"])

with tab2:
    st.subheader(t["rank_subheader"])
    if not st.session_state.df.empty:
        display_df = st.session_state.df.copy()
        if '複雜度評分' in display_df.columns:
            display_df = display_df.sort_values(by='複雜度評分', ascending=False)
            display_df.insert(0, t['col_rank'], range(1, len(display_df) + 1))
            final_display = display_df.rename(columns={
                "序號": t["col_seq"], 
                "複雜度評分": t["col_score"],
                "個體數": t["col_entities"],
                "系統數": t["col_systems"]
            })
            st.dataframe(final_display, hide_index=True, use_container_width=True)
            
            st.divider()
            csv_data = final_display.to_csv(index=False).encode('utf-8-sig')
            st.download_button(label=t["btn_download"], data=csv_data, file_name="Complexity_Report.csv", mime="text/csv")
        else:
            st.warning(t["warn_no_score"])
            st.dataframe(display_df.rename(columns={"序號": t["col_seq"]}), hide_index=True, use_container_width=True)