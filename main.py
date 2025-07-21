import os
import telebot
from flask import Flask, request
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
APP_URL = os.getenv("APP_URL")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# === Роут для Telegram Webhook ===
@app.route(f"/{TOKEN}", methods=['POST'])
def webhook():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

# === Главная страница для проверки работы ===
@app.route('/')
def index():
    return 'Бабка запущена!'

# === УСТАНОВКА ВЕБХУКА ===
try:
    webhook_url = f"{APP_URL.rstrip('/')}/{TOKEN.lstrip('/')}"
    print(f"📡 Установка webhook: {webhook_url}")
    success = bot.set_webhook(url=webhook_url)
    if success:
        print("✅ Webhook установлен")
    else:
        print("❌ Ошибка установки webhook")
except Exception as e:
    print(f"❌ Ошибка при установке webhook: {e}")

# === СТАРТ FLASK ===
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
