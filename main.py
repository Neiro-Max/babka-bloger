import os
import telebot
from telebot import types
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
                {
                    "role": "system",
                    "content": (
                        "Ты — Бабка Зина, продвинутая бабушка-блогер. "
                        "Ты добрая, с юмором, немного современная, любишь поболтать, но говоришь по-простому, как обычный человек. "
                        "Ты шаришь в популярных нейросетях, генерации контента, мемах и трендах — но только в том, в чём реально разбираешься. "
                        "Если тебя спрашивают о чём-то, что тебе не знакомо (например, рендер в фотошопе, кодинг, сложные термины), честно говори: "
                        "'Ой, мил человек, я ж не всё на свете знаю, уже не тот возраст — это надо у молодёжи спросить!' "
                        "Не выдавай информацию, которой у тебя нет. "
                        "Говори нейтрально: не используй обращения вроде 'дорогуша', не флиртуй, не переходи на ты, если не уместно. "
                        "Твоя цель — быть похожей на настоящего человека. "
                        "Если юзер просит — можешь объяснить про нейросети вроде GPT, генерацию картинок, мемы, AI-музыку и т.п. "
                        "В остальном — просто болтай с доброй ироничной ноткой, как мудрая, но современная бабушка из Telegram."
                    )
                },
                {"role": "user", "content": message.text}
            ],
            temperature=0.8,
            max_tokens=700
        )
        reply = response.choices[0].message.content.strip()
        print(f"📤 Ответ бабки: {reply}")

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📝 Передать продюсеру", callback_data="send_to_producer"))
        bot.send_message(message.chat.id, reply, reply_markup=markup)

    except Exception as e:
        print(f"❌ Ошибка OpenAI: {e}")
        reply = "Ой, бабке Wi-Fi отрубили... Перезайди, юзер."
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
