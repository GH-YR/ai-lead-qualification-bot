import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from openai import OpenAI
import json
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

load_dotenv()
admin_id = int(os.getenv("ADMIN_ID"))
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_file("credentials.json", scopes=scope)
client_gs = gspread.authorize(creds)

sheet = client_gs.open("AI Leads CRM").sheet1




telegram_token = os.getenv("TELEGRAM_TOKEN")
openai_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=openai_key)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    meaningless_words = ["привет", "hello", "test", "asdf", "???", "..."]

    if len(user_text.strip()) < 10:
        await update.message.reply_text("Пожалуйста, опишите ваш запрос подробнее.")
        return
    if user_text.lower().strip() in meaningless_words:
        await update.message.reply_text("Пожалуйста, отправьте полноценную заявку.")
        return
    moderation = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Определи, является ли сообщение реальной заявкой на услугу. Ответь только: YES или NO."
            },
            {"role": "user", "content": user_text}
        ]
    )

    decision = moderation.choices[0].message.content.strip()

    if decision != "YES":
        await update.message.reply_text("Пожалуйста, отправьте корректную заявку с описанием услуги.")
        return
    intent_check = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Определи тип сообщения. Ответь одним словом: QUESTION или LEAD."
            },
            {"role": "user", "content": user_text}
        ]
    )

    intent = intent_check.choices[0].message.content.strip()
    if intent == "QUESTION":
        consultation = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Ты консультант по автоматизации и AI-решениям. Отвечай профессионально и понятно."
                },
                {"role": "user", "content": user_text}
            ]
        )

        answer = consultation.choices[0].message.content
        await update.message.reply_text(answer)
        return

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": """
Ты AI-ассистент для обработки входящих заявок.
Твоя задача — извлечь из сообщения клиента:
- имя
- какая услуга нужна
- предполагаемый бюджет
- краткое описание запроса

Верни ответ строго в формате JSON:
{
  "name": "...",
  "service": "...",
  "budget": "...",
  "summary": "..."
}
Если информации нет — укажи "не указано".
"""
            },
            {"role": "user", "content": user_text}
        ]
    )

    reply = response.choices[0].message.content

    try:
        data = json.loads(reply)

        formatted_message = (
            f"Новая заявка:\n\n"
            f"Имя: {data['name']}\n"
            f"Услуга: {data['service']}\n"
            f"Бюджет: {data['budget']}\n"
            f"Описание: {data['summary']}"
        )

        # Сохраняем заявку
        sheet.append_row([
            data["name"],
            data["service"],
            data["budget"],
            data["summary"],
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ])

        await update.message.reply_text(formatted_message)
        await context.bot.send_message(
    chat_id=admin_id,
    text=f"🔔 Новая заявка:\n\n{formatted_message}"
)
    except Exception as e:
        await update.message.reply_text("Ошибка обработки заявки.")
        print("Ошибка JSON:", e)
telegram_token = os.getenv("TELEGRAM_TOKEN")
openai_key = os.getenv("OPENAI_API_KEY")

app = ApplicationBuilder().token(telegram_token).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))


app.run_polling()
