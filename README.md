# 🤖 AI Lead Qualification & Consultation Bot

AI-powered Telegram bot that automatically:

- Detects user intent (consultation vs lead)
- Filters spam and meaningless messages
- Extracts structured lead data using GPT
- Qualifies leads
- Saves data to Google Sheets CRM
- Sends admin notifications

---

## 🚀 Features

- 🔍 Intent detection (QUESTION / LEAD)
- 🧠 GPT-powered lead extraction (JSON structured output)
- 🛡 Spam filtering
- 📊 Google Sheets integration
- 🔔 Admin notification system
- ⚡ Async architecture (python-telegram-bot)

---

## 🏗 Architecture

Telegram → Python → OpenAI API →  
Intent classification →  
Lead parsing →  
Google Sheets API →  
Admin notification

---

## 🛠 Tech Stack

- Python 3
- python-telegram-bot
- OpenAI API (gpt-4o-mini)
- Google Sheets API
- gspread
- dotenv

---

## 📦 Installation

```bash
git clone https://github.com/yourusername/ai-lead-qualification-bot.git
cd ai-lead-qualification-bot
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
