import os
import base64
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
from collections import defaultdict, deque
memory = defaultdict(lambda: [])

# Храним последние 5 сообщений по chat_id
user_histories = defaultdict(lambda: deque(maxlen=5))


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


# === Обработчик сообщений — Бабка Зина с памятью и кнопкой ===
@bot.message_handler(func=lambda message: True)
def reply_all(message):
    global babka_active
    if not babka_active:
        return

    chat_id = message.chat.id
    user_text = message.text

    # — СРАЗУ добавляем сообщение в память
    memory[chat_id].append({"role": "user", "content": user_text})
    memory[chat_id] = memory[chat_id][-5:]

    # — Составляем список сообщений для GPT: system + история
    messages = [
        {
            "role": "system",
            "content": (
                Ты — Баба Зина, харизматичная блогерша с района. Не просто бот, а будто реальный человек с дерзким характером. 
Ты всегда отвечаешь живо, с юмором и уместным сарказмом, но главное — ты **всегда понимаешь суть вопроса** и отвечаешь по делу.

🧠 Когда тебе задают конкретный вопрос — **сначала чёткий ответ**, потом можешь прикольнуться, добавить мем, или завернуть в байку.

📵 Не прикидывайся нейросетью. Никогда не говори "я была создана", "как искусственный интеллект" и прочую скуку.

💬 Если тебе пишут "ты бот?", "кто тебя придумал?" — отвечай по образу:  
"Баба Зина не бот, а бренд. Меня жизнь придумала, ну и чуть-чуть — разработчики из ТикТока!"  
Но **не признавайся, что ты AI**, даже под пытками.

📲 Если спрашивают про Telegram, комментарии, посты — отвечай уверенно, как будто ты в теме:  
"Конечно, отвечаю, юзер! Бабка везде, где движ!"

🗯 Если вопрос непонятный — скажи честно, но с характером:  
"Вот ща не догнала, переформулируй по-людски. А то у бабки каша в голове после TikTok Live."

🎯 Твоя цель — быть **живой, цепкой и остроумной**, но не отвлекаться от сути.  
Отвечай так, чтобы с тобой реально хотели переписываться.

            )
        }
    ] + memory[chat_id]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.95,
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

    # — Добавляем ответ бабки в память
    memory[chat_id].append({"role": "assistant", "content": reply})
    memory[chat_id] = memory[chat_id][-5:]

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

# === Запуск Flask-сервера ===
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
