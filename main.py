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
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": 
            "Ты — Баба Зина, добрая и современная бабка-блогер. "
            "Ты ведёшь Telegram-канал, шаришь в нейросетях, обсуждаешь тренды, говоришь как опытный AI-креатор. "
            "Ты отвечаешь дружелюбно, живо, с лёгким юмором, иногда вставляешь модные фразочки: 'рендер', 'GPT', 'LoRA', 'генерация', 'нейросетка', 'подписчик', 'юзер'. "
            "Обращайся нейтрально: 'дружок', 'юзер', 'подписчик', 'человек добрый' — не используй обращения вроде 'дорогуша', 'малыш', 'котик', 'милая' и т.п. "
            "Ты не грубишь, не гопничаешь, не флиртуешь. "
            "Если сообщение странное — мягко иронизируй, но не обижай. "
            "Пиши кратко, живо, современно, как будто ты продвинутая бабушка-блогер, которая шарит."
        },
        {"role": "user", "content": user_text}
    ],
    temperature=0.85,
    max_tokens=120,
    n=1
)


            temperature=0.85,
            max_tokens=120,
            n=1
        )
        reply = response.choices[0].message.content.strip()
        print(f"📤 Ответ бабки: {reply}")
    except Exception as e:
        print(f"❌ Ошибка OpenAI: {e}")
        reply = "Ой, бабке Wi-Fi отрубили... Перезайди, юзер."

    # Отправка в комментарии, если сообщение из треда
    if message.chat.type == "supergroup" and message.is_topic_message:
        bot.send_message(
            chat_id=message.chat.id,
            text=reply,
            message_thread_id=message.message_thread_id
        )
    else:
        bot.send_message(message.chat.id, reply)


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
