from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def send_welcome_users(message , bot):
    name = message.from_user.first_name

    markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    contact_button = KeyboardButton('📞 Send Contact', request_contact=True)
    markup.add(contact_button)

    welcome_message = f"""
    🇺🇿
Salom {name} 👋
CodeVan servicega xush kelibsiz
⬇️ Kontaktingizni yuboring va 10 daqiqalik kalitingizni oling!

🇺🇸
Hi {name} 👋
Welcome to CodeVan service
⬇️ Send your contact and get 10 minutes key!
"""
    bot.send_message(message.chat.id, welcome_message, reply_markup=markup)


def send_welcome_admin(message , bot):
    name = message.from_user.first_name
    welcome_message = f"""
    Salom {name}. Siz tizimda admin rolidasiz menga rasmlarni yuboring va men uni sizga hashlangan holatda qaytaraman. Keyin ushbu rasmdan test uchun foydalansangiz bo'ladi.
"""
    bot.send_message(message.chat.id, welcome_message)
