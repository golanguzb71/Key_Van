import threading

from flask import Flask, request, jsonify

from helpers.helpers import bot, handle_contact_helper, send_welcome_helper, handle_renew_helper
from utils.utils import process_doc

app = Flask(__name__)

@app.route('/getTestTextFile', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        print(file.filename)
        return process_doc(file, file.filename)


def run_flask():
    app.run(host='0.0.0.0', port=5000)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    send_welcome_helper(message)


@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    handle_contact_helper(message)


@bot.callback_query_handler(func=lambda call: call.data.startswith('renew_'))
def handle_renew(call):
    handle_renew_helper(call)


def run_bot():
    bot.polling()


if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    run_bot()
