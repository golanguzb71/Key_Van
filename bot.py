import telebot
import psycopg2
import redis
import random
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from config.config import BOT_TOKEN, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DATABASE, POSTGRES_HOST, POSTGRES_PORT, \
    REDIS_HOST, REDIS_PORT
from utils.utils import find_key_by_value

bot = telebot.TeleBot(BOT_TOKEN)

conn = psycopg2.connect(
    dbname=POSTGRES_DATABASE,
    user=POSTGRES_USER,
    password=POSTGRES_PASSWORD,
    host=POSTGRES_HOST,
    port=POSTGRES_PORT
)
cur = conn.cursor()

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


def generate_code():
    return random.randint(10000, 99999)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    name = message.from_user.first_name

    markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    contact_button = KeyboardButton('📞 Send Contact', request_contact=True)
    markup.add(contact_button)

    welcome_message = f"""
🇺🇿
Salom {name} 👋
Camelotning rasmiy botiga xush kelibsiz

⬇️ Kontaktingizni yuboring (tugmani bosib)

🇺🇸
Hi {name} 👋
Welcome to Camelot's official bot

⬇️ Send your contact (by clicking button)
"""
    bot.send_message(message.chat.id, welcome_message, reply_markup=markup)


@bot.message_handler(content_types=['contact'])
def handle_contact(message):
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
    # data = {'user_id': user_id, 'code': code}
    # redis_client.setex(chat_id, 600, json.dumps(data))
    redis_client.setex(code, 300, chat_id)

    markup = InlineKeyboardMarkup()
    renew_button = InlineKeyboardButton('🔄 Yangilash / Renew', callback_data=f'renew_{code}_{chat_id}')
    markup.add(renew_button)

    bot.send_message(
        chat_id,
        f"🔒 Code: <code>{code}</code>",
        parse_mode='HTML',
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith('renew_'))
def handle_renew(call):
    code, chat_id = map(int, call.data.split('_')[1:])
    existing_data = redis_client.get(code)
    if existing_data is not None:
        bot.send_message(call.message.chat.id, "Eski kodingiz hali ham kuchda ☝️")
        return

    new_code = generate_code()
    # new_data = {'user_id': user_id, 'code': new_code}
    # redis_client.setex(chat_id, 600, json.dumps(new_data))  # Store for 10 minutes
    redis_client.setex(code, 300, chat_id)
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"🔒 Code: <code>{new_code}</code>",
        parse_mode='HTML',
        reply_markup=call.message.reply_markup
    )


if __name__ == "__main__":
    bot.polling()
