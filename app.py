import streamlit as st
import pandas as pd
from collections import Counter

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="Supersootr Analyzer V2", page_icon="📊")

# ==========================================
# 1. ข้อมูลดิบ (Raw Data)
# ==========================================
# (ผมย่อข้อมูลบางส่วนเพื่อความกระชับ แต่ในการใช้งานจริง ให้ใช้ข้อมูลครบชุดจากไฟล์เดิมของคุณ)
raw_data = [
    ("2024-01-02", "02956243934493853"), ("2024-01-03", "03985835586526276"),
    ("2024-01-04", "05896689450125997"), ("2024-01-05", "02768243580799663"),
    ("2024-01-08", "07125544233634551"), ("2024-01-09", "04297894424799352"),
    ("2024-01-10", "02271147959665241"), ("2024-01-11", "00957589402502428"),
    ("2024-01-12", "05834593585615329"), ("2024-01-15", "09946742146070251"),
    ("2024-01-16", "07230267630727230"), ("2024-01-17", "03537462686866507"),
    # ... (คุณสามารถก็อปปี้ list raw_data ทั้งหมดจากไฟล์เดิมมาใส่ตรงนี้ได้เลยครับ) ...
    ("2026-01-14", "07141926294643000"), ("2026-01-15", "08842007018883909"),
    ("2026-01-16", "07366773881426021"), ("2026-01-19", "04181448431712060"),
]
# หมายเหตุ: เพื่อให้โค้ดรันได้ทันที ผมใส่ข้อมูลตัวอย่างล่าสุดไว้ ถ้าจะใช้จริงจัง ให้ Copy raw_data ทั้งก้อนจากไฟล์เดิมมาทับตรงนี้ครับ

position_map = {
    0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e', 5: 'f', 6: 'g', 7: 'h', 8: 'i',
    9: 'j', 10: 'k', 11: 'l', 12: 'm', 13: 'n', 14: 'o', 15: 'p', 16: 'q'
}

char_to_index = {v: k for k, v in position_map.items() if k != 0}

pair_to_indices = {
    'bc': [1, 2], 'de': [3, 4], 'fg': [5, 6], 'hi': [7, 8],
    'jk': [9, 10], 'lm': [11, 12], 'no': [13, 14], 'pq': [15, 16]
}

pos_desc = {
    'b': 'หลักสิบ-เปิดเช้า', 'c': 'หลักหน่วย-เปิดเช้า',
    'd': 'หลักสิบ-เปิดล่างเช้า', 'e': 'หลักหน่วย-เปิดล่างเช้า',
    'f': 'หลักสิบ-ปิดเที่ยง', 'g': 'หลักหน่วย-ปิดเที่ยง',
    'h': 'หลักสิบ-ปิดล่างเที่ยง', 'i': 'หลักหน่วย-ปิดล่างเที่ยง',
    'j': 'หลักสิบ-เปิดบ่าย', 'k': 'หลักหน่วย-เปิดบ่าย',
    'l': 'หลักสิบ-เปิดล่างบ่าย', 'm': 'หลักหน่วย-เปิดล่างบ่าย',
    'n': 'หลักสิบ-ปิดเย็น', 'o': 'หลักหน่วย-ปิดเย็น',
    'p': 'หลักสิบ-ปิดล่างเย็น', 'q': 'หลักหน่วย-ปิดล่างเย็น',
    'bc': 'วิ่งสิบหน่วยบน-เปิดเช้า', 'de': 'วิ่งสิบหน่วยล่าง-เปิดเช้า',
    'fg': 'วิ่งสิบหน่วยบน-ปิดเที่ยง', 'hi': 'วิ่งสิบหน่วยล่าง-ปิดเที่ยง',
    'jk': 'วิ่งสิบหน่วยบน-เปิดบ่าย', 'lm': 'วิ่งสิบหน่วยล่าง-เปิดบ่าย',
    'no': 'วิ่งสิบหน่วยบน-ปิดเย็น', 'pq': 'วิ่งสิบหน่วยล่าง-ปิดเย็น'
}

# ==========================================
# 2. ฟังก์ชันวิเคราะห์ (Logic เดิม)
# ==========================================

def get_digit(data_row, index):
    return int(data_row[1][index])

def calculate_prediction(draw, indices, k):
    total = sum(get_digit(draw, idx) for idx in indices)
    return (total + k) % 10

# ใช้ cache เพื่อให้เว็บไม่คำนวณใหม่ทุกครั้งที่กดปุ่มเล็กๆ น้อยๆ
@st.cache_data
def find_formulas(mode, target_indices, history_data, lookback_rounds, max_formulas, min_accuracy):
    results = []
    total_positions = 17

    if len(history_data) < lookback_rounds + 1:
        return []

    test_data = history_data[-(lookback_rounds+1):]
    total_test_rounds = len(test_data) - 1
    max_misses = int(total_test_rounds * (1 - (min_accuracy / 100)))

    # สูตร 2 ตัว
    for x in range(1, total_positions):
        for y in range(x, total_positions):
            for k in range(10):
                miss_count = 0
                indices = [x, y]
                for i in range(total_test_rounds):
                    prediction = calculate_prediction(test_data[i], indices, k)
                    if mode == 'kill':
                        actual = get_digit(test_data[i+1], target_indices[0])
                        if prediction == actual: miss_count += 1
                    elif mode == 'run':
                        actuals = [get_digit(test_data[i+1], idx) for idx in target_indices]
                        if prediction not in actuals: miss_count += 1
                    if miss_count > max_misses: break
                
                if miss_count <= max_misses:
                    accuracy = ((total_test_rounds - miss_count) / total_test_rounds) * 100
                    results.append({'indices': indices, 'k': k, 'misses': miss_count, 'accuracy': accuracy, 'description': f"{position_map[x]} + {position_map[y]} + {k}"})

    # สูตร 3 ตัว
    for x in range(1, total_positions):
        for y in range(x, total_positions):
            for z in range(y, total_positions):
                for k in range(10):
                    miss_count = 0
                    indices = [x, y, z]
                    for i in range(total_test_rounds):
                        prediction = calculate_prediction(test_data[i], indices, k)
                        if mode == 'kill':
                            actual = get_digit(test_data[i+1], target_indices[0])
                            if prediction == actual: miss_count += 1
                        elif mode == 'run':
                            actuals = [get_digit(test_data[i+1], idx) for idx in target_indices]
                            if prediction not in actuals: miss_count += 1
                        if miss_count > max_misses: break
                    
                    if miss_count <= max_misses:
                        accuracy = ((total_test_rounds - miss_count) / total_test_rounds) * 100
                        results.append({'indices': indices, 'k': k, 'misses': miss_count, 'accuracy': accuracy, 'description': f"{position_map[x]} + {position_map[y]} + {position_map[z]} + {k}"})

    results.sort(key=lambda item: item['accuracy'], reverse=True)
    return results[:max_formulas]

# ==========================================
# 3. ส่วนแสดงผล (UI)
# ==========================================
st.title("💰 Supersootr Analyzer V2")
st.markdown("ระบบวิเคราะห์เลข **ดับ** และ **วิ่ง** (Multi-Mode)")

# Sidebar สำหรับตั้งค่า
with st.sidebar:
    st.header("⚙️ ตั้งค่าการคำนวณ")
    lookback = st.slider("จำนวนงวดย้อนหลัง (Lookback)", 30, 200, 70)
    formula_limit = st.slider("จำกัดจำนวนสูตร (Max Formulas)", 100, 3000, 1000)
    
    st.markdown("---")
    st.info(f"ข้อมูลล่าสุด: {raw_data[-1][0]}")

# เลือกโหมดหลัก
mode_choice = st.radio("เลือกโหมด", ["1. หาเลขดับ (Killing)", "2. หาเลขวิ่ง (Running)"], horizontal=True)
target_mode = 'kill' if "Killing" in mode_choice else 'run'

# เลือกเป้าหมาย (Dropdown)
if target_mode == 'kill':
    min_acc_default = 90.0
    options = list(char_to_index.keys())
    # สร้าง label สวยๆ ให้ Dropdown
    format_func = lambda x: f"{x} - {pos_desc.get(x, '')}"
    selected_pos = st.selectbox("เลือกตำแหน่งที่ต้องการหาเลขดับ", options, format_func=format_func, index=12) # Default 'n'
    target_indices = [char_to_index[selected_pos]]
    target_name = f"เลขดับหลัก: {selected_pos.upper()}"
else:
    min_acc_default = 75.0
    options = list(pair_to_indices.keys())
    format_func = lambda x: f"{x} - {pos_desc.get(x, '')}"
    selected_pos = st.selectbox("เลือกคู่ตำแหน่งที่ต้องการหาเลขวิ่ง", options, format_func=format_func, index=6) # Default 'no'
    target_indices = pair_to_indices[selected_pos]
    target_name = f"เลขวิ่งคู่: {selected_pos.upper()}"

min_accuracy = st.number_input("ความแม่นยำขั้นต่ำ (%)", min_value=50.0, max_value=100.0, value=min_acc_default, step=0.5)

# ปุ่มคำนวณ
if st.button("🚀 เริ่มวิเคราะห์สูตร", type="primary"):
    with st.spinner('กำลังประมวลผลสูตรนับพัน... กรุณารอสักครู่...'):
        formulas = find_formulas(target_mode, target_indices, raw_data, lookback, formula_limit, min_accuracy)
    
    if not formulas:
        st.error("ไม่พบสูตรที่เข้าเกณฑ์เลย! ลองลดความแม่นยำลง หรือเปลี่ยนตำแหน่ง")
    else:
        st.success(f"พบสูตรเดินดีจำนวน: {len(formulas)} สูตร")
        
        # คำนวณผลงวดถัดไป
        last_draw = raw_data[-1]
        next_numbers = []
        
        # แสดงตัวอย่างสูตร
        with st.expander("ดูรายการสูตร (Top 10)"):
            top_formulas = []
            for f in formulas:
                pred_num = calculate_prediction(last_draw, f['indices'], f['k'])
                next_numbers.append(pred_num)
                top_formulas.append({
                    "สูตร": f['description'],
                    "ความแม่นยำ": f"{f['accuracy']:.2f}%",
                    "ผิด (งวด)": f['misses'],
                    "ผลลัพธ์งวดนี้": pred_num
                })
            st.table(pd.DataFrame(top_formulas[:10]))

        # สรุปผล
        st.markdown("---")
        st.header(f"🏆 ผลวิเคราะห์: {target_name}")
        
        stats = Counter(next_numbers)
        # เติม 0 ให้ครบ 0-9 เพื่อกราฟสวย
        for d in range(10):
            if d not in stats: stats[d] = 0
            
        df_stats = pd.DataFrame.from_dict(stats, orient='index', columns=['Count'])
        df_stats.index.name = 'Number'
        df_stats = df_stats.sort_values(by='Count', ascending=False)
        
        # หาเลขเด่นสุด
        best_num = df_stats.index[0]
        max_score = df_stats.iloc[0]['Count']
        percent = (max_score / len(formulas)) * 100
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.metric(label="ฟันธงเลข", value=str(best_num), delta=f"{percent:.1f}% Confidence")
            if target_mode == 'kill':
                st.caption("คือเลขที่คาดว่าจะ **ไม่มา**")
            else:
                st.caption("คือเลขที่คาดว่าจะ **มา**")
                
        with col2:
            st.bar_chart(df_stats)

        st.dataframe(df_stats.T)