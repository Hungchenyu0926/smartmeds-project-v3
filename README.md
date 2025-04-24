# 💊 SmartMeds-AI

使用 **Streamlit + OpenAI + Google Sheets** 的 AI 藥師照護建議工具。

## 🚀 快速開始
```bash
git clone https://github.com/<your-user>/smartmeds-project.git
cd smartmeds-project
pip install -r requirements.txt
streamlit run app.py
```

## 🗝️ Secrets 設定
將 `.streamlit/secrets.toml` 內容貼到本機或 Streamlit Cloud *App→Secrets*。**切勿提交至 GitHub**。

## 📑 Google Sheet 欄位
| 姓名 | 年齡 | 性別 | 疾病 | 目前用藥 | 審核藥師 | 藥師風險判讀 | 修正意見 | 照護時間 |
|------|------|------|------|----------|----------|--------------|----------|----------|
