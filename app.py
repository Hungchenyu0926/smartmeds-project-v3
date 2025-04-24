import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from openai import OpenAI
from datetime import datetime

st.set_page_config(page_title="SmartMeds-AI", page_icon="💊", layout="centered")
st.title("💊 SmartMeds-AI｜用藥建議與交互作用小幫手")

# ---------- Google Sheets 認證 ----------
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds_dict = st.secrets["GSPREAD_CREDENTIALS"]
credentials = Credentials.from_service_account_info(creds_dict, scopes=scope)
gs_client = gspread.authorize(credentials)
sheet = gs_client.open("SmartMeds_DB").sheet1

# ---------- OpenAI client ----------
openai_client = OpenAI(api_key=st.secrets["OPENAI"]["api_key"])

def get_drug_advice(drug_list, age, conditions):
    prompt = (
        "你是資深臨床藥師，需依 2023 Beers Criteria 與 2022 STOPP/START v3 "
        "針對下列資訊給出用藥安全分析與建議，格式：\n"
        "1. 潛在問題\n2. 機制/風險\n3. 建議替代方案/監測\n4. 參考來源 (Beers/STOPP)。\n"
        f"年齡: {age} 歲\n"
        f"病史: {', '.join(conditions) if conditions else '無'}\n"
        f"藥品: {', '.join(drug_list)}\n"
        "請以繁體中文分段回答。"
    )
    resp = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    return resp.choices[0].message.content

# ---------- 使用者介面 ----------
drug_input = st.text_input("🔎 請輸入藥品名稱（多項請以逗號分隔）")
age = st.number_input("👤 年齡", min_value=1, max_value=120, value=65)
cond_input = st.text_input("🩺 病史或慢性疾病（多項請以逗號分隔，可留空）")

if st.button("📋 生成用藥建議"):
    drugs = [d.strip() for d in drug_input.split(",") if d.strip()]
    conditions = [c.strip() for c in cond_input.split(",") if c.strip()]
    if not drugs:
        st.warning("請輸入至少一個藥品名稱。")
        st.stop()

    with st.spinner("AI 努力分析中..."):
        try:
            advice = get_drug_advice(drugs, age, conditions)
            st.markdown(advice)

            sheet.append_row([
                None,
                age,
                None,
                ", ".join(conditions),
                ", ".join(drugs),
                "AI",
                "自動判讀",
                advice,
                datetime.utcnow().isoformat()
            ])
        except Exception as e:
            st.error(f"🛑 發生錯誤：{e}")
