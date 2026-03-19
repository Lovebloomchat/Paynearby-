import os
import telebot
from playwright.sync_api import sync_playwright

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise Exception("BOT_TOKEN missing")

bot = telebot.TeleBot(TOKEN)

URL = "https://retailerportal.paynearby.in/auth/login?source=paynearby-site"

LOGIN_NUMBER = "9973028650"
LOGIN_PASSWORD = "Shubham@9282"


def check_numbers(numbers):
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = browser.new_page()

        # login once
        page.goto(URL)
        page.fill("input[type='tel']", LOGIN_NUMBER)
        page.fill("input[type='password']", LOGIN_PASSWORD)
        page.click("button")

        page.wait_for_timeout(10000)

        for num in numbers:
            try:
                page.fill("input[type='tel']", "")
                page.fill("input[type='tel']", num)

                page.wait_for_timeout(1200)

                content = page.content().lower()

                if "not registered" not in content:
                    results.append(num)

            except:
                pass

        browser.close()

    return results


# ✅ SAFE FILE SENDER (NO ERROR EVER)
def send_result(chat_id, result):
    with open("result.txt", "w") as f:
        f.write("\n".join(result))

    with open("result.txt", "rb") as f:
        bot.send_document(chat_id, f)


# START
@bot.message_handler(commands=['start'])
def start(msg):
    bot.reply_to(msg, "Send numbers or .txt file")


# TEXT INPUT
@bot.message_handler(content_types=['text'])
def handle_text(message):
    try:
        if message.text.startswith("/"):
            return

        bot.reply_to(message, "⏳ Processing...")

        numbers = [x.strip() for x in message.text.split() if x.strip()]

        result = check_numbers(numbers)

        send_result(message.chat.id, result)

    except Exception as e:
        bot.reply_to(message, "Error occurred")


# FILE INPUT
@bot.message_handler(content_types=['document'])
def handle_file(message):
    try:
        bot.reply_to(message, "⏳ Processing file...")

        file_info = bot.get_file(message.document.file_id)
        file = bot.download_file(file_info.file_path)

        with open("input.txt", "wb") as f:
            f.write(file)

        with open("input.txt") as f:
            numbers = [line.strip() for line in f if line.strip()]

        result = check_numbers(numbers)

        send_result(message.chat.id, result)

    except Exception as e:
        bot.reply_to(message, "Error occurred")


print("🚀 BOT STARTED")
bot.infinity_polling(timeout=60, long_polling_timeout=60)
