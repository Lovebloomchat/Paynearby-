import requests
from telegram import Update, InputFile
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import os

TOKEN = os.getenv("BOT_TOKEN")


def check_number(num):
    url = f"https://pnbapi.paynearby.in/v1/retailers/lookup?phone_number={num}"
    try:
        r = requests.get(url, timeout=5)

        if r.status_code == 200:
            return "REGISTERED"
        elif r.status_code == 404:
            return "NOT REGISTERED"
        else:
            return "UNKNOWN"
    except:
        return "ERROR"


def start(update: Update, context: CallbackContext):
    update.message.reply_text("📂 Send .txt file with numbers")


def handle_file(update: Update, context: CallbackContext):
    file = update.message.document

    if not file.file_name.endswith(".txt"):
        update.message.reply_text("❌ Send only .txt file")
        return

    update.message.reply_text("⏳ Processing started...")

    file_path = "input.txt"
    output_path = "output.txt"

    file.get_file().download(file_path)

    results = []

    with open(file_path, "r") as f:
        numbers = f.read().splitlines()

    for num in numbers:
        num = num.strip()
        if num:
            status = check_number(num)
            results.append(f"{num} : {status}")

    # output file bana
    with open(output_path, "w") as f:
        f.write("\n".join(results))

    update.message.reply_document(document=open(output_path, "rb"))


def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.document, handle_file))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
