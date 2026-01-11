import streamlit as st
import pandas as pd
import os
import plotly.express as px

# --- 1. 語言配置字典 ---
PAGE_LANG = {
    "繁體中文": {
        "page_title": "案件投報率分析",
        "main_title": "💰 案件投報率分析",
        "warn_no_master": "⚠️ 尚未偵測到主資料評分結果。",
        "tabs": ["📋 1. 報價資訊填寫", "🔍 2. 投報率分析總覽"],
        "tab1_header": "📋 報價資訊填寫",
        "msg_missing": "🚩 **提醒：尚有 {} 個案件未填寫報價金額**",
        "msg_all_filled": "✅ 所有案件報價皆已填寫完成！",
        "op_tip": " **操作提醒**：修改後請點擊下方儲存按鈕。若 Excel 檔案開啟中將無法儲存。",
        "col_name": "案件名稱",
        "col_complexity": "複雜度評分",
        "col_price": "最終報價(萬)",
        "col_hours": "預計工時",
        "btn_save": "💾 儲存商務數據並更新全案分析",
        "msg_save_success": "✅ 商務數據已成功儲存！",
        "msg_save_fail": "❌ 儲存失敗！請先關閉 Excel 檔案 (`roi_data.xlsx`)。",
        "col_roi": "投報率",
        "col_eval": "商務評價",
        "roi_label": "ROI (萬/分)",
        "eval_high": "🟢 效益高於平均",
        "eval_low": "🔴 效益低於平均",
        "list_header": "🔍 案件投報率分析清單",
        "roi_standard": "**判定標準**：投報率大於平均值 **{:.2f}** 即為利多。",
        "matrix_header": "📊 商務決策矩陣 (釐清異常)",
        "plot_x": "技術難度",
        "plot_y": "金額 (萬)",
        "avg_price_line": "平均報價",
        "avg_diff_line": "平均難度",
        "decision_header": "🚩 管理決策建議",
        "warn_raise_price": "⚠️ **應提高報價案件**",
        "success_no_issue": "✅ 暫無異常案件。",
        "star_cases": "💎 **優質核心案件**",
        "matrix_info": "💡 請先在頁簽 1 填寫報價金額後即可查看分析矩陣。"
    },
    "English": {
        "page_title": "Business Decision System",
        "main_title": "💰 Case ROI Analysis",
        "warn_no_master": "⚠️ No master data scores detected.",
        "tabs": ["📋 1. Pricing Entry", "🔍 2. ROI Overview"],
        "tab1_header": "📋 Pricing Information Entry",
        "msg_missing": "🚩 **Alert: {} cases pending price entry**",
        "msg_all_filled": "✅ All prices have been entered!",
        "op_tip": " **Note**: Click save after editing. Ensure Excel is closed.",
        "col_name": "Case Name",
        "col_complexity": "Complexity Score",
        "col_price": "Final Quote (10k)",
        "col_hours": "Est. Hours",
        "btn_save": "💾 Save Business Data & Update Analysis",
        "msg_save_success": "✅ Data saved successfully!",
        "msg_save_fail": "❌ Save failed! Close `roi_data.xlsx` first.",
        "col_roi": "ROI",
        "col_eval": "Evaluation",
        "roi_label": "ROI (10k/pt)",
        "eval_high": "🟢 Above Avg Benefit",
        "eval_low": "🔴 Below Avg Benefit",
        "list_header": "🔍 Case ROI Analysis List",
        "roi_standard": "**Standard**: Benefit > Avg **{:.2f}** is considered Gain.",
        "matrix_header": "📊 Business Decision Matrix (Outliers)",
        "plot_x": "Technical Difficulty",
        "plot_y": "Amount (10k)",
        "avg_price_line": "Avg Price",
        "avg_diff_line": "Avg Difficulty",
        "decision_header": "🚩 Management Suggestions",
        "warn_raise_price": "⚠️ **Underpriced Cases**",
        "success_no_issue": "✅ No anomalies found.",
        "star_cases": "💎 **Premium Core Cases**",
        "matrix_info": "💡 Please fill in prices in Tab 1 to view the matrix."
    }
}

# 取得語系
curr_lang = st.session_state.get("lang", "繁體中文")
t = PAGE_LANG[curr_lang]

# 1. 系統配置
st.set_page_config(page_title=t["page_title"], layout="wide")

current_dir = os.path.dirname(os.path.abspath(__file__))
output_folder = os.path.join(os.path.dirname(current_dir), "outputs")
MASTER_FILE = os.path.join(output_folder, "master_data.xlsx")
ROI_FILE = os.path.join(output_folder, "roi_data.xlsx")

# 2. 資料載入
def load_data():
    master_df = pd.read_excel(MASTER_FILE).copy() if os.path.exists(MASTER_FILE) else pd.DataFrame()
    roi_df = pd.read_excel(ROI_FILE).copy() if os.path.exists(ROI_FILE) else pd.DataFrame()
    return master_df, roi_df

st.title(t["main_title"])
master_df, roi_df = load_data()

if master_df.empty:
    st.warning(t["warn_no_master"])
else:
    # 3. 資料整合與同步
    sync_data = master_df[['案件名稱', '複雜度評分']].copy()
    if not roi_df.empty:
        if '最終報價' in roi_df.columns and '最終報價(萬)' not in roi_df.columns:
            roi_df = roi_df.rename(columns={'最終報價': '最終報價(萬)'})
        valid_cols = [c for c in ['案件名稱', '最終報價(萬)', '預計工時'] if c in roi_df.columns]
        sync_data = pd.merge(sync_data, roi_df[valid_cols], on='案件名稱', how='left')
    
    sync_data['最終報價(萬)'] = sync_data['最終報價(萬)'].fillna(0.0)
    sync_data['預計工時'] = sync_data['預計工時'].fillna(0.0)

    # --- 建立頁簽 ---
    tab1, tab2 = st.tabs(t["tabs"])

    with tab1:
        st.subheader(t["tab1_header"])
        
        missing_price = sync_data[sync_data['最終報價(萬)'] <= 0]['案件名稱'].tolist()
        if missing_price:
            st.warning(t["msg_missing"].format(len(missing_price)))
            cols = st.columns(3)
            for idx, name in enumerate(missing_price):
                cols[idx % 3].caption(f"• {name}")
        else:
            st.success(t["msg_all_filled"])
        
        st.info(t["op_tip"])
        
        # 數據編輯區 (翻譯欄位名稱)
        edited_df = st.data_editor(
            sync_data.rename(columns={
                "案件名稱": t["col_name"], "複雜度評分": t["col_complexity"],
                "最終報價(萬)": t["col_price"], "預計工時": t["col_hours"]
            }),
            column_config={
                t["col_name"]: st.column_config.Column(disabled=True),
                t["col_complexity"]: st.column_config.NumberColumn(t["col_complexity"], disabled=True),
                t["col_price"]: st.column_config.NumberColumn(t["col_price"], min_value=0, format="%f"),
                t["col_hours"]: st.column_config.NumberColumn(t["col_hours"], min_value=0),
            },
            hide_index=True, 
            use_container_width=True, 
            key="roi_editor"
        )

        if st.button(t["btn_save"], use_container_width=True):
            try:
                # 轉回原始 Key 存檔
                save_df = edited_df.rename(columns={
                    t["col_name"]: "案件名稱", t["col_complexity"]: "複雜度評分",
                    t["col_price"]: "最終報價(萬)", t["col_hours"]: "預計工時"
                })
                save_df.to_excel(ROI_FILE, index=False)
                st.success(t["msg_save_success"])
                st.rerun()
            except PermissionError:
                st.error(t["msg_save_fail"])

    with tab2:
        # 還原 Key 以進行計算
        calc_df = edited_df.rename(columns={
            t["col_name"]: "案件名稱", t["col_complexity"]: "複雜度評分",
            t["col_price"]: "最終報價(萬)", t["col_hours"]: "預計工時"
        }).copy()
        
        calc_df['投報率'] = calc_df.apply(
            lambda x: round(x['最終報價(萬)'] / x['複雜度評分'], 2) if x['複雜度評分'] > 0 else 0, axis=1
        )
        
        active_mask = calc_df['最終報價(萬)'] > 0
        avg_roi = calc_df.loc[active_mask, '投報率'].mean() if active_mask.any() else 0
        avg_price = calc_df.loc[active_mask, '最終報價(萬)'].mean() if active_mask.any() else 0
        avg_complexity = calc_df['複雜度評分'].mean()

        calc_df['商務評價'] = calc_df['投報率'].apply(
            lambda x: t["eval_high"] if x >= avg_roi and x > 0 else t["eval_low"]
        )

        st.subheader(t["list_header"])
        st.info(t["roi_standard"].format(avg_roi))
        
        st.dataframe(
            calc_df[['案件名稱', '複雜度評分', '最終報價(萬)', '投報率', '商務評價']].rename(columns={
                "案件名稱": t["col_name"], "複雜度評分": t["col_complexity"],
                "最終報價(萬)": t["col_price"], "投報率": t["col_roi"], "商務評價": t["col_eval"]
            }),
            column_config={t["col_roi"]: st.column_config.NumberColumn(t["roi_label"], format="%.2f")},
            hide_index=True, 
            use_container_width=True
        )

        st.divider()

        if active_mask.any():
            st.subheader(t["matrix_header"])
            plot_df = calc_df[active_mask].copy()
            fig = px.scatter(
                plot_df, x='複雜度評分', y='最終報價(萬)',
                size='投報率', color='商務評價',
                text='案件名稱', hover_name='案件名稱',
                color_discrete_map={t["eval_high"]: "#00CC96", t["eval_low"]: "#EF553B"},
                labels={'複雜度評分': t["plot_x"], '最終報價(萬)': t["plot_y"]},
                height=500
            )
            # 輔助線翻譯
            fig.add_hline(y=avg_price, line_dash="dash", annotation_text=t["avg_price_line"])
            fig.add_vline(x=avg_complexity, line_dash="dash", annotation_text=t["avg_diff_line"])
            st.plotly_chart(fig, use_container_width=True)

            st.subheader(t["decision_header"])
            bad_cases = calc_df[(calc_df['複雜度評分'] > avg_complexity) & (calc_df['最終報價(萬)'] < avg_price) & active_mask]
            col1, col2 = st.columns(2)
            with col1:
                if not bad_cases.empty:
                    st.error(f"{t['warn_raise_price']}\n\n" + "\n".join([f"- {name}" for name in bad_cases['案件名稱']]))
                else: st.success(t["success_no_issue"])
            with col2:
                star_cases = calc_df[(calc_df['複雜度評分'] < avg_complexity) & (calc_df['最終報價(萬)'] > avg_price)]
                if not star_cases.empty:
                    st.success(f"{t['star_cases']}\n\n" + "\n".join([f"- {name}" for name in star_cases['案件名稱']]))
        else:
            st.info(t["matrix_info"])