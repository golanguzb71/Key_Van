import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from config.config import BOT_TOKEN
from database.postgres import cur, conn
from database.redisClient import redis_client
from helpers.extraHelpers import send_welcome_users
from utils.utils import find_key_by_value, generate_code

bot = telebot.TeleBot(BOT_TOKEN)


def send_welcome_helper(message):
    send_welcome_users(message, bot)


def handle_contact_helper(message):
    chat_id = message.chat.id
    contact = message.contact
    phone_number = contact.phone_number
    first_name = contact.first_name
    last_name = contact.last_name

    # existing_data = redis_client.get(chat_id)
    existing_data = find_key_by_value(redis_client, chat_id)
    if existing_data is not None:
        bot.send_message(
            chat_id,
            text=f"""
            Eski kodingiz hali ham kuchda ☝️
            <code>{existing_data}</code>
            """,
            parse_mode='HTML'
        )
        return

    if phone_number[0] != "+":
        phone_number = "+" + phone_number

    cur.execute("SELECT id FROM users WHERE phone_number = %s", (phone_number,))
    user_record = cur.fetchone()

    if user_record:
        user_id = user_record[0]
        if last_name is not None:
            cur.execute(
                "UPDATE users SET full_name = %s WHERE id = %s",
                (f"{first_name} {last_name}", user_id)
            )
        else:
            cur.execute(
                "UPDATE users SET full_name = %s WHERE id = %s",
                (first_name, user_id)
            )
        conn.commit()
    else:
        if last_name is not None:
            cur.execute(
                "INSERT INTO users (phone_number, full_name, chat_id) VALUES (%s, %s ,%s);",
                (phone_number, f"{first_name} {last_name}", chat_id)
            )
        else:
            cur.execute(
                "INSERT INTO users (full_name, phone_number , chat_id) VALUES (%s, %s , %s);",
                (first_name, phone_number, chat_id)
            )
        conn.commit()
    code = generate_code()
    # database = {'user_id': user_id, 'code': code}
    # redis_client.setex(chat_id, 600, json.dumps(database))
    redis_client.setex(code, 600, chat_id)

    markup = InlineKeyboardMarkup()
    renew_button = InlineKeyboardButton('🔄 Yangilash / Renew', callback_data=f'renew_{code}_{chat_id}')
    markup.add(renew_button)

    bot.send_message(
        chat_id,
        f"🔒 Code: <code>{code}</code>",
        parse_mode='HTML',
        reply_markup=markup
    )


def handle_renew_helper(call):
    code, chat_id = map(int, call.data.split('_')[1:])
    existing_data = redis_client.get(code)
    if existing_data is not None:
        bot.send_message(call.message.chat.id, f"Eski kodingiz hali ham kuchda ☝️ {code}")
        return

    new_code = generate_code()
    # new_data = {'user_id': user_id, 'code': new_code}
    # redis_client.setex(chat_id, 600, json.dumps(new_data))  # Store for 10 minutes
    redis_client.setex(new_code, 600, chat_id)
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"🔒 Code: <code>{new_code}</code>",
        parse_mode='HTML',
        reply_markup=call.message.reply_markup
    )
