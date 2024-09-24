import threading
import time
from flask import Flask, request, jsonify
from helpers.helpers import bot, handle_contact_helper, send_welcome_helper, handle_renew_helper
from utils.utils import process_doc
from requests.exceptions import ReadTimeout


@bot.message_handler(commands=['start'])
def send_welcome(message):
    send_welcome_helper(message)


@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    handle_contact_helper(message)


@bot.callback_query_handler(func=lambda call: call.data.startswith('renew_'))
def handle_renew(call):
    handle_renew_helper(call)


app = Flask(__name__)


@app.route('/getTestTextFile', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        return process_doc(file, file.filename)


def run_flask():
    try:
        app.run(host='0.0.0.0', port=5000)
    except Exception as e:
        print(f"Error running Flask server: {e}")


def run_bot():
    while True:
        try:
            bot.polling(timeout=60, long_polling_timeout=60)
        except ReadTimeout:
            print("Bot polling timed out. Retrying in 5 seconds...")
            time.sleep(5)
        except Exception as e:
            print(f"An error occurred in the bot: {e}")
            time.sleep(5)

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    run_bot()
