import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import openai, json
from datetime import datetime

# ---------- Secrets ----------
openai.api_key = st.secrets["OPENAI"]["api_key"]

google_keys = [
    "type","project_id","private_key_id","private_key","client_email",
    "client_id","auth_uri","token_uri",
    "auth_provider_x509_cert_url","client_x509_cert_url"
]
creds_dict = {k: st.secrets[k] for k in google_keys}
credentials = Credentials.from_service_account_info(creds_dict, scopes=[
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
])
gc = gspread.authorize(credentials)

SHEET_NAME = "SmartMeds_DB"
worksheet = gc.open(SHEET_NAME).sheet1

st.set_page_config(page_title="SmartMeds-AI", page_icon="💊")
st.title("💊 SmartMeds-AI｜AI藥師照護建議")

drug_query = st.text_input("🔍 搜尋藥品名稱（可多個，以逗號分隔）")
age = st.number_input("🎂 年齡", 0, 120, step=1)
history_input = st.text_area("🩺 病史或慢性疾病（可多個，以逗號分隔）")

if st.button("生成用藥建議"):
    meds = [m.strip() for m in drug_query.split(",") if m.strip()]
    histories = [h.strip() for h in history_input.split(",") if h.strip()]

    if not meds:
        st.warning("請輸入至少一個藥品名稱")
        st.stop()

    system_prompt = (
        "你是資深臨床藥師，需依 2023 Beers Criteria 與 2022 STOPP/START v3 "
        "就病人年齡、病史與查詢藥品提供建議，"
        "格式：(1) 潛在問題 (2) 機制/風險 (3) 建議替代方案與監測 (4) 參考來源。"
        "請用繁體中文作答。"
    )
    user_prompt = f"年齡:{age} 歲\n病史:{', '.join(histories)}\n查詢藥品:{', '.join(meds)}"

    try:
        rsp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
        )
        advice = rsp.choices[0].message.content
    except Exception as e:
        st.error(f"OpenAI 發生錯誤：{e}")
        st.stop()

    st.subheader("📑 AI藥師建議")
    st.markdown(advice)

    # --- 回寫 Google Sheet ---
    worksheet.append_row([
        None,         # 姓名
        age if age else None,
        None,         # 性別
        ", ".join(histories) if histories else None,
        ", ".join(meds),
        "AI",
        "自動判讀",
        advice,
        datetime.utcnow().isoformat()
    ])
