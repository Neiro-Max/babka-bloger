import os
import telebot
from dotenv import load_dotenv

load_dotenv()
bot = telebot.TeleBot(os.getenv("TELEGRAM_BOT_TOKEN"))

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    # Игнорируем сообщения не из групп-комментариев
    if message.chat.type not in ['group', 'supergroup']:
        return

    # Игнорируем сообщения самого бота
    if message.from_user is None or message.from_user.id == bot.get_me().id:
        return

    # Проверка: если это комментарий к посту (reply_to_message — пост канала)
    is_comment = (
        message.reply_to_message is not None and
        message.reply_to_message.forward_from_chat is not None and
        message.reply_to_message.forward_from_chat.type == 'channel'
    )

    # Если это комментарий — бабка отвечает прямо на него
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

        # Отвечаем именно на комментарий
        bot.send_message(
            chat_id=message.chat.id,
            text=reply,
            reply_to_message_id=message.message_id
        )

print("Бабка-Блогер запущена!")
bot.infinity_polling()
