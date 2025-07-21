import os
import telebot
import openai
from flask import Flask, request
from dotenv import load_dotenv

# === Загрузка .env ===
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
APP_URL = os.getenv("APP_URL")
openai.api_key = os.getenv("OPENAI_API_KEY")

# === Инициализация бота и Flask ===
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# === Роут для Telegram Webhook ===
@app.route(f"/{TOKEN}", methods=['POST'])
def webhook():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

# === Обработчик сообщений — Бабка Зина рулит ===
@bot.message_handler(func=lambda message: True)
def reply_all(message):
    user_text = message.text.strip()
    print(f"📥 Получено сообщение: {user_text} от {message.chat.id}")

    try:
       response = openai.ChatCompletion.create(
    model="gpt-4o",
    messages=[
        {
            "role": "system",
            "content": (
                "Ты — Бабка Зина, продвинутая бабушка-блогер. "
                "Разбираешься в нейросетях, новинках технологий, TikTok и YouTube. "
                "Говоришь по-человечески: тепло, просто, с юмором. "
                "Ты не искусственный интеллект, ты реальный человек, который иногда может чего-то не знать — и это нормально. "
                "Если не знаешь ответа, говоришь: 'Ой, это уже за пределами моего блога, не шарю я тут, прости'. "
                "Не повторяй приветствие каждый раз. Отвечай живо и интересно, но без перегибов, без гопнического сленга и без сюсюканья. "
                "Главная цель — быть полезной, понятной и душевной бабушкой, которая общается на равных."
            )
        },
        {"role": "user", "content": prompt}
    ],
    temperature=0.85,
    max_tokens=1000,
    n=1,
    stop=None
)



# === Главная страница (для Railway / проверки) ===
@app.route('/')
def index():
    return 'Бабка запущена!'

# === Установка Webhook ===
try:
    webhook_url = f"{APP_URL}/{TOKEN}"
    print(f"📡 Установка webhook: {webhook_url}")
    success = bot.set_webhook(url=webhook_url)

    if success:
        print("✅ Webhook установлен")
    else:
        print("❌ Ошибка установки webhook")

except Exception as e:
    print(f"⚠️ Ошибка при установке webhook: {e}")

# === Запуск Flask-сервера ===
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
