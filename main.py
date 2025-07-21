import os
import telebot
from flask import Flask, request
from random import choice

# === НАСТРОЙКИ ===
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
APP_URL = os.getenv("APP_URL")  # Пример: https://your-app-name.up.railway.app
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# === УСТАНОВКА ВЕБХУКА ===
def setup_webhook():
    bot.remove_webhook()
    bot.set_webhook(url=f"{APP_URL}/{TOKEN}")

# === ПОЛУЧЕНИЕ СООБЩЕНИЙ ОТ TELEGRAM ===
@app.route(f"/{TOKEN}", methods=["POST"])
def receive_update():
    json_string = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "OK", 200

# === СТИЛЬ: БЛОГЕРСКАЯ БАБКА ===
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user_name = message.from_user.first_name or "подписчик"
    replies = [
        f"Эй, {user_name}, ты чё тут пишешь? Бабка шарит, не кипишуй 😎",
        f"Слышь, {user_name}, у бабки свой вайб! 👵🔥",
        f"Ты — {user_name}? Ну, норм, с тобой базар можно вести.",
    ]
    bot.send_message(message.chat.id, choice(replies))

# === СТАРТ ПРИ ЗАПУСКЕ ===
if __name__ == "__main__":
    setup_webhook()  # Устанавливаем вебхук перед запуском
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
