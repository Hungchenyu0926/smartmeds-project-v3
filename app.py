import streamlit as st
import gspread
from openai import OpenAI
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

st.set_page_config(page_title="SmartMeds-AI", page_icon="💊", layout="centered")
st.title("💊 SmartMeds-AI 用藥建議與交互作用小幫手")

# ---------- Google Sheets 認證 ----------
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["GSPREAD_CREDENTIALS"], scope)
gs_client = gspread.authorize(creds)
sheet = gs_client.open("SmartMeds_DB").sheet1

# ---------- OpenAI client ----------
openai_client = OpenAI(api_key=st.secrets["OPENAI"]["api_key"])

def get_drug_advice(drug_list, age, conditions):
    prompt = (
        "你是一位資深臨床藥師，請依 2023 Beers Criteria 與 2022 STOPP/START v3，"
        "對下列資訊提供用藥安全建議，格式：\n"
        "1. 潛在問題 2. 機制/風險 3. 建議替代方案/監測 4. 參考來源 (Beers/STOPP)。\n"
        f"年齡: {age} 歲\n"
        f"病史: {', '.join(conditions) if conditions else '無'}\n"
        f"藥品: {', '.join(drug_list)}\n"
        "回答請用繁體中文，分段清晰呈現。"
    )
    resp = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
    )
    return resp.choices[0].message.content

# ---------- UI ----------
drug_input = st.text_input("🔎 請輸入藥品名稱（多項以逗號分隔）")
age = st.number_input("👤 年齡", min_value=1, max_value=120, value=65)
cond_input = st.text_input("🩺 病史或慢性疾病（多項以逗號分隔，可留空）")

if st.button("📋 生成用藥建議"):
    drugs = [d.strip() for d in drug_input.split(",") if d.strip()]
    conditions = [c.strip() for c in cond_input.split(",") if c.strip()]
    if not drugs:
        st.warning("請輸入至少一個藥品名稱。")
        st.stop()

    with st.spinner("AI 分析中..."):
        try:
            advice = get_drug_advice(drugs, age, conditions)
            st.markdown(advice)

            # -------- 回寫 Google Sheet --------
            sheet.append_row([
                None,                   # 姓名
                age,
                None,                   # 性別
                ", ".join(conditions),  # 疾病
                ", ".join(drugs),       # 目前用藥
                "AI",                   # 審核藥師
                "自動判讀",              # 藥師風險判讀
                advice,                 # 修正意見
                datetime.utcnow().isoformat()  # 照護時間
            ])
        except Exception as e:
            st.error(f"🛑 發生錯誤：{e}")
