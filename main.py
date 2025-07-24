import openai
from flask import Flask, request
from dotenv import load_dotenv
from collections import defaultdict, deque

# === Загрузка .env ===
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
APP_URL = os.getenv("APP_URL")
openai.api_key = os.getenv("OPENAI_API_KEY")
from collections import defaultdict, deque
memory = defaultdict(lambda: [])

# Храним последние 5 сообщений по chat_id
user_histories = defaultdict(lambda: deque(maxlen=5))


# === Инициализация бота и Flask ===
bot = telebot.TeleBot(TOKEN)
babka_active = True  # Бабка включена по умолчанию
ADMIN_ID = 1034982624  # Твой Telegram ID

babka_active = True
ADMIN_ID = 1034982624
app = Flask(__name__)

# === Память бабки (до 5 реплик на чат)
memory = defaultdict(lambda: deque(maxlen=5))

# === Роут для Telegram Webhook ===
@app.route(f"/{TOKEN}", methods=['POST'])
def webhook():
@@ -38,9 +35,8 @@ def webhook():
def handle_send_to_producer(call):
    bot.answer_callback_query(call.id, "Бабка всё передала продюсеру 🎤")

    # Обновляем кнопку
    new_markup = telebot.types.InlineKeyboardMarkup()
    new_markup.add(telebot.types.InlineKeyboardButton("📝 Передано продюсеру", callback_data="none"))
    new_markup.add(types.InlineKeyboardButton("📝 Передано продюсеру", callback_data="none"))
    bot.edit_message_reply_markup(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
@@ -50,10 +46,7 @@ def handle_send_to_producer(call):
    producer_id = 1034982624
    user_id = call.from_user.id
    username = call.from_user.username
    if username:
        user_tag = f"@{username}"
    else:
        user_tag = f"{call.from_user.first_name or 'Пользователь'} (ID: {user_id})"
    user_tag = f"@{username}" if username else f"{call.from_user.first_name or 'Пользователь'} (ID: {user_id})"

    try:
        encoded_text = call.data.split("|", 1)[1]
@@ -67,9 +60,9 @@ def handle_send_to_producer(call):
        f"👤 От: {user_tag}\n"
        f"💬 Текст: {decoded_text}"
    )

    bot.send_message(producer_id, alert, parse_mode="HTML")
    # === Команды включения/выключения бабки ===

# === Команды включения/выключения бабки ===
@bot.message_handler(commands=['on'])
def turn_on_babka(message):
    global babka_active
@@ -88,74 +81,54 @@ def turn_off_babka(message):
    else:
        bot.send_message(message.chat.id, "⛔ Только админ может выключать Бабку.")


# === Обработчик сообщений — Бабка Зина с памятью и кнопкой ===
# === Обработчик сообщений — Бабка Зина умнеет ===
@bot.message_handler(func=lambda message: True)
def reply_all(message):
    global babka_active
    if not babka_active:
        return

    chat_id = message.chat.id
    user_text = message.text.strip()

    tech_triggers = ["нейросеть", "нейро", "бот", "openai", "gpt", "интернет", "чат", "ai", "алгоритм", "обучение", "пост", "комментарий"]
    is_tech = any(trigger in user_text.lower() for trigger in tech_triggers)

    history = memory[chat_id][-4:]
    # — Сохраняем сообщение пользователя до GPT
    memory[chat_id].append({"role": "user", "content": user_text})

    # — Формируем список сообщений
    messages = [
        {
            "role": "system",
            "content": (
                "Ты - Баба Зина, блогерша с характером. Всегда говоришь по делу, но с юмором. "
                "Можешь отвечать на любые вопросы, в том числе про технологии, Telegram, нейросети и т.д. "
                "Отвечай как умная, дерзкая женщина, не уходи от ответа, не трать время на болтовню, если юзер спрашивает по делу."
                "Ты — Баба Зина, умная, дерзкая и весёлая блогерша. "
                "Ты отвечаешь по делу, но с характером и приколом. "
                "Если вопрос серьёзный — сначала по существу, потом можно добавить шуточку. "
                "Если непонятно — скажи честно, но с юмором. "
                "Отвечай как человек, не как бот. Можешь обсуждать нейросети, Telegram, ботов, технологии и всё, что спросит юзер."
            )
        }
    ]

    if is_tech:
        messages.append({
            "role": "user",
            "content": "Вопрос про технологии, Telegram, нейросети или комментарии. Объясни по-бабкиному."
        })

    messages += history + [{"role": "user", "content": user_text}]
    ] + list(memory[chat_id])

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.95,
            temperature=0.85,
            max_tokens=700
        )
        reply = response.choices[0].message.content.strip()
        if not reply:
            reply = "Ой, милота, что-то не догнала... Повтори, пожалуйста!"
    except Exception as e:
        print(f"❌ Ошибка OpenAI: {e}")
        import traceback
        traceback.print_exc()
        reply = "Ой, бабке Wi-Fi отрубили... Перезайди, юзер."

    # — Фильтрация пустых фраз, чтобы не сохранять в память
    skip_phrases = ["привет", "але", "ты тут", "ты где", "бабуся", "бабка", "слышишь"]
    if user_text.lower() not in skip_phrases:
        memory[chat_id].append({"role": "user", "content": user_text})
        memory[chat_id].append({"role": "assistant", "content": reply})
        memory[chat_id] = memory[chat_id][-5:]
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
@@ -166,16 +139,13 @@ def index():
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
# === Запуск Flask-сервера с threaded ===
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), threaded=True)
