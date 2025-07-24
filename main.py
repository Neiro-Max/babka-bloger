import os
import base64
import telebot
from telebot import types
import openai
from flask import Flask, request
from dotenv import load_dotenv
from collections import defaultdict

# История сообщений по каждому юзеру
user_histories = defaultdict(list)
MAX_HISTORY = 5  # сколько последних сообщений запоминаем
def update_history(user_id, message_text):
    user_histories[user_id].append(message_text)
    if len(user_histories[user_id]) > MAX_HISTORY:
        user_histories[user_id] = user_histories[user_id][-MAX_HISTORY:]



# === Загрузка .env ===
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
APP_URL = os.getenv("APP_URL")
openai.api_key = os.getenv("OPENAI_API_KEY")
import random

# Стили поведения бабки
babushka_styles = [
    "Ты — Бабка Зина. Дерзкая, язвительная, разговариваешь как гопник с района.",
    "Ты — Бабка Зина. С юмором, по-доброму троллишь юзеров, шутишь и прикалываешься.",
    "Ты — Бабка Зина. Материшься в меру, без перебора, но не стесняешься словечек.",
    "Ты — Бабка Зина. Говоришь как мудрая уличная старушка, но шаришь в мемах и нейросетях.",
    "Ты — Бабка Зина. Ответы даёшь в стиле блогера из TikTok: иронично, современно, с приколами.",
    "Ты — Бабка Зина. Резкая, но справедливая. Отвечаешь как есть, без фильтров и лести.",
    "Ты — Бабка Зина. Весёлая, саркастичная, говоришь как живой человек, не как робот.",
    "Ты — Бабка Зина. Без гендерных обращений. Только нейтральные: юзер, человек, подписчик."
]


# === Инициализация бота и Flask ===
bot = telebot.TeleBot(TOKEN)
babka_active = True  # Бабка включена по умолчанию
ADMIN_ID = 1034982624  # Твой Telegram ID

app = Flask(__name__)

# === Роут для Telegram Webhook ===
@app.route(f"/{TOKEN}", methods=['POST'])
def webhook():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

# === Обработчик callback-кнопки "Передать продюсеру" ===
@bot.callback_query_handler(func=lambda call: call.data.startswith("send_to_producer"))
def handle_send_to_producer(call):
    bot.answer_callback_query(call.id, "Бабка всё передала продюсеру 🎤")

    # Обновляем кнопку
    new_markup = telebot.types.InlineKeyboardMarkup()
    new_markup.add(telebot.types.InlineKeyboardButton("📝 Передано продюсеру", callback_data="none"))
    bot.edit_message_reply_markup(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=new_markup
    )

    producer_id = 1034982624
    user_id = call.from_user.id
    username = call.from_user.username
    if username:
        user_tag = f"@{username}"
    else:
        user_tag = f"{call.from_user.first_name or 'Пользователь'} (ID: {user_id})"

    try:
        encoded_text = call.data.split("|", 1)[1]
        decoded_text = base64.b64decode(encoded_text.encode()).decode()
    except Exception as e:
        print(f"❌ Ошибка декодирования: {e}")
        decoded_text = "⚠️ Не удалось расшифровать сообщение."

    alert = (
        f"🎬 Бабка передала сообщение продюсеру!\n\n"
        f"👤 От: {user_tag}\n"
        f"💬 Текст: {decoded_text}"
    )

    bot.send_message(producer_id, alert, parse_mode="HTML")
    # === Команды включения/выключения бабки ===
@bot.message_handler(commands=['on'])
def turn_on_babka(message):
    global babka_active
    if message.from_user.id == ADMIN_ID:
        babka_active = True
        bot.send_message(message.chat.id, "🟢 Бабка включена и снова в строю!")
    else:
        bot.send_message(message.chat.id, "⛔ Только админ может включать Бабку.")

@bot.message_handler(commands=['off'])
def turn_off_babka(message):
    global babka_active
    if message.from_user.id == ADMIN_ID:
        babka_active = False
        bot.send_message(message.chat.id, "🔇 Бабка замолкла. Пока что.")
    else:
        bot.send_message(message.chat.id, "⛔ Только админ может выключать Бабку.")



# === Обработчик сообщений — Бабка Зина рулит ===
@bot.message_handler(func=lambda message: True)
def reply_all(message):
    if not babka_active:
        return

    user_text = message.text.strip()
    print(f"📥 Получено сообщение: {user_text} от {message.chat.id}")

    try:
        # Случайный стиль бабки
        random_style = random.choice(babushka_styles)

        # Обновляем историю пользователя
        update_history(message.from_user.id, user_text)

        # Формируем цепочку сообщений для GPT
        chat_history = [
            {"role": "system", "content": (
                f"{random_style} "
                "Отвечай по-человечески, без заученных фраз. "
                "Если вопрос не по теме — шути, но не молчи. "
                "Не используй обращений по полу — ни 'дорогая', ни 'милок'. "
                "Только нейтральные слова: юзер, подписчик, человек."
            )}
        ]

        for msg in user_histories[message.from_user.id]:
            chat_history.append({"role": "user", "content": msg})

        # Отправляем запрос к GPT
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=chat_history,
            temperature=1.0,
            max_tokens=700
        )
        reply = response.choices[0].message.content.strip()
                if not reply or len(reply) < 3:
            reply = "Я тебе не Википедия, юзер. Но чё-то ты мудришь конкретно..."


    except Exception as e:
        print(f"❌ Ошибка OpenAI: {e}")
        reply = "Ой, бабке Wi-Fi отрубили... Перезайди, юзер."

    # Кнопка "Передать продюсеру"
    encoded_text = base64.b64encode(user_text.encode()).decode()
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📝 Передать продюсеру", callback_data=f"send_to_producer|{encoded_text}"))

    bot.send_message(message.chat.id, reply, reply_markup=markup)


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
