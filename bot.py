from helpers.helpers import bot, handle_contact_helper, send_welcome_helper, handle_renew_helper


@bot.message_handler(commands=['start'])
def send_welcome(message):
    send_welcome_helper(message)


@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    handle_contact_helper(message)


@bot.callback_query_handler(func=lambda call: call.data.startswith('renew_'))
def handle_renew(call):
    handle_renew_helper(call)


if __name__ == "__main__":
    bot.polling()
