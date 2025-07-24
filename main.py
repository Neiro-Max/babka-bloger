import os
import base64
import telebot
from telebot import types
import openai
from flask import Flask, request
from dotenv import load_dotenv
from collections import defaultdict, deque

# === Загрузка .env ===
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
APP_URL = os.getenv("APP_URL")
openai.api_key = os.getenv("OPENAI_API_KEY")

# === Инициализация бота и Flask ===
bot = telebot.TeleBot(TOKEN)
babka_active = True
ADMIN_ID = 1034982624
app = Flask(__name__)

# === Память бабки (до 5 реплик на чат)
memory = defaultdict(lambda: deque(maxlen=5))

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

    new_markup = telebot.types.InlineKeyboardMarkup()
    new_markup.add(types.InlineKeyboardButton("📝 Передано продюсеру", callback_data="none"))
    bot.edit_message_reply_markup(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=new_markup
    )

    producer_id = 1034982624
    user_id = call.from_user.id
    username = call.from_user.username
    user_tag = f"@{username}" if username else f"{call.from_user.first_name or 'Пользователь'} (ID: {user_id})"

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

# === Обработчик сообщений — Бабка Зина умнеет ===
@bot.message_handler(func=lambda message: True)
def reply_all(message):
    if not babka_active:
        return

    if message.from_user.id not in ALLOWED_USERS:
        return


    chat_id = message.chat.id
    user_text = message.text.strip()

    # — Сохраняем сообщение пользователя до GPT
    memory[chat_id].append({"role": "user", "content": user_text})

    # — Формируем список сообщений
    messages = [
        {
            "role": "system",
            "content": (
                "Ты — Баба Зина, умная, дерзкая и весёлая блогерша. "
                "Ты отвечаешь по делу, но с характером и приколом. "
                "Если вопрос серьёзный — сначала по существу, потом можно добавить шуточку. "
                "Если непонятно — скажи честно, но с юмором. "
                "Отвечай как человек, не как бот. Можешь обсуждать нейросети, Telegram, ботов, технологии и всё, что спросит юзер."
            )
        }
    ] + list(memory[chat_id])

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.85,
            max_tokens=700
        )
        reply = response.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ Ошибка OpenAI: {e}")
        reply = "Ой, бабке Wi-Fi отрубили... Перезайди, юзер."

    # — Сохраняем ответ бабки в память
    memory[chat_id].append({"role": "assistant", "content": reply})

    # — Кнопка "Передать продюсеру"
    encoded_text = base64.b64encode(user_text.encode()).decode()
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📝 Передать продюсеру", callback_data=f"send_to_producer|{encoded_text}"))

    bot.send_message(chat_id, reply, reply_markup=markup)

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

# === Запуск Flask-сервера с threaded ===
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), threaded=True)
