import os
import telebot
from flask import Flask, request
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
APP_URL = os.getenv("APP_URL")  # Пример: https://babka-bloger-production.up.railway.app

if not TOKEN or not APP_URL:
    raise ValueError("TOKEN или APP_URL не задан в переменных окружения")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# === Обработка сообщений ===
@bot.message_handler(func=lambda m: True)
def handle_message(message):
    if message.chat.type in ['group', 'supergroup']:
        bot.send_message(
            message.chat.id,
            "🧓 Бабка что-то буркнула!",
            reply_to_message_id=message.message_id
        )

# === Webhook-обработка ===
@app.route(f"/{TOKEN}", methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.data.decode("utf-8"))
    bot.process_new_updates([update])
    return "ok", 200

# === Запуск приложения ===
if __name__ == "__main__":
    bot.remove_webhook()
    webhook_url = f"{APP_URL}/{TOKEN}"
    print("Пробуем установить вебхук:", webhook_url)

    success = bot.set_webhook(url=webhook_url)
    if success:
        print("✅ Вебхук установлен успешно.")
    else:
        print("❌ Не удалось установить вебхук.")

    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
