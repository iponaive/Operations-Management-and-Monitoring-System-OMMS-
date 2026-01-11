import pandas as pd
import numpy as np

def calculate_complexity(df):
    """
    優化版評分邏輯：
    1. 使用向量化運算 (Vectorization) 確保效能。
    2. 自動將空值 (NaN) 視為 0 或 '否'。
    3. 對齊 Excel 的正確欄位名稱。
    """
    df_result = df.copy()

    # --- 內部工具：確保數值欄位空值補 0 ---
    def get_num(col_name):
        return pd.to_numeric(df_result.get(col_name), errors='coerce').fillna(0)

    # --- 內部工具：判斷「是/否」，空值與非「是」皆不加分 ---
    def get_bool_score(col_name, points):
        # 轉為字串並去除前後空格
        condition = df_result.get(col_name).astype(str).str.strip() == '是'
        return np.where(condition, points, 0)

    # 1. 規模與系統架構
    # 邏輯：優先採用「實際系統數」，若為 0 則採計「系統數」
    actual_sys = get_num('(系統)已考量共用情況之實際系統數')
    raw_sys = get_num('系統數')
    final_sys = np.where(actual_sys > 0, actual_sys, raw_sys)

    score = (get_num('個體數') * 2) + (final_sys * 4)

    # 2. 基礎特性與風險
    # 判斷是否「不共用」系統 (+3)
    share_cond = df_result.get('個體是否共用系統').astype(str).str.strip() == '否'
    score += np.where(share_cond, 3, 0)
    
    score += get_bool_score('系統是否客製化', 3)
    score += get_bool_score('是否被Q', 8)
    score += get_bool_score('是否為PCAOB', 10)
    score += get_bool_score('前期負責PM是否更換',5)

    # 3. IPO 專項加權
    ipo_col = df_result.get('IPO送件類型').astype(str)
    ipo_conditions = [
        ipo_col.str.contains('上市'),
        ipo_col.str.contains('上櫃'),
        ipo_col.str.contains('興櫃')
    ]
    ipo_choices = [5, 4, 2]
    score += np.select(ipo_conditions, ipo_choices, default=0)

    score += get_bool_score('IPO是否為複雜資安', 7)
    score += get_bool_score('IPO是否首查', 5)

    # 4. ITAC 工作量與各項首查
    score += (get_num('ITAC題數') * 1.5)
    score += get_bool_score('ITAC是否首查', 8)
    score += get_bool_score('GC是否首查', 5)
    score += get_bool_score('Caats是否首查', 6)

    # 寫入計算結果
    df_result['複雜度評分'] = score
    
    # 依分數高低排序並回傳
    return df_result.sort_values(by='複雜度評分', ascending=False)