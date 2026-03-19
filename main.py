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

        # LOGIN
        page.goto(URL)
        page.fill("input[type='tel']", LOGIN_NUMBER)
        page.fill("input[type='password']", LOGIN_PASSWORD)
        page.click("button")

        for _ in range(12):
            page.wait_for_timeout(1000)

        # LOOP
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


@bot.message_handler(commands=['start'])
def start(msg):
    bot.reply_to(msg, "Send numbers OR .txt file")


# ✅ TEXT INPUT
@bot.message_handler(func=lambda message: message.content_type == "text")
def handle_text(message):
    try:
        bot.reply_to(message, "⏳ Checking...")

        numbers = [x.strip() for x in message.text.split() if x.strip()]

        result = check_numbers(numbers)

        if not result:
            bot.reply_to(message, "❌ No registered numbers")
            return

        with open("result.txt", "w") as f:
            f.write("\n".join(result))

        with open("result.txt", "rb") as f:
            bot.send_document(message.chat.id, f)

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")


# ✅ FILE INPUT (.txt)
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

        if not result:
            bot.reply_to(message, "❌ No registered numbers")
            return

        with open("result.txt", "w") as f:
            f.write("\n".join(result))

        with open("result.txt", "rb") as f:
            bot.send_document(message.chat.id, f)

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")


print("🚀 BOT STARTED")
bot.infinity_polling(timeout=60, long_polling_timeout=60)
