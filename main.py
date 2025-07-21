import os
import telebot
from flask import Flask, request
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
APP_URL = os.getenv("APP_URL")  # должен начинаться с https://
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# === Логика бабки ===
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    if message.chat.type not in ['group', 'supergroup']:
        return

    if message.from_user is None or message.from_user.id == bot.get_me().id:
        return

    is_comment = (
        message.reply_to_message is not None and
        message.reply_to_message.forward_from_chat is not None and
        message.reply_to_message.forward_from_chat.type == 'channel'
    )

    if is_comment:
        user_message = message.text.lower()
        if "привет" in user_message:
            reply = "Привет, сынок. Чего хотел?"
        elif "как дела" in user_message:
            reply = "Да нормально, пенсию получила, сижу тут в Telegram, как модная."
        elif "что нового" in user_message:
            reply = "А ты бы лучше новости сам почитал, а то я тебе сейчас наговорю!"
        else:
            reply = "Ты по делу или просто так поболтать со старой бабкой?"

        bot.send_message(
            chat_id=message.chat.id,
            text=reply,
            reply_to_message_id=message.message_id
        )

# === Webhook setup ===
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "ok", 200

# === При запуске — установка вебхука ===
@app.before_first_request
def setup_webhook():
    bot.remove_webhook()
    bot.set_webhook(url=f"{APP_URL}/{TOKEN}")

print("Бабка-Блогер запущена через вебхук!")
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
