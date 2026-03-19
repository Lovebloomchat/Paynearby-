import os
import telebot
from playwright.sync_api import sync_playwright

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise Exception("BOT_TOKEN missing")

bot = telebot.TeleBot(TOKEN)

URL = "https://retailerportal.paynearby.in/auth/login?source=paynearby-site"


def check_numbers(numbers):
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = browser.new_page()

        # open page
        page.goto(URL)

        # activate session (1 time)
        page.fill("input[type='tel']", "9999999999")
        page.fill("input[type='password']", "test123")
        page.click("button")

        # short wait (max 15 sec)
        for i in range(15):
            page.wait_for_timeout(1000)

        # loop
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
    bot.reply_to(msg, "Send numbers or .txt")


# 🔥 DIRECT NUMBER INPUT SUPPORT
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    try:
        bot.reply_to(message, "⏳ Checking...")

        # numbers split
        numbers = [x.strip() for x in message.text.split() if x.strip()]

        result = check_numbers(numbers)

        if not result:
            bot.reply_to(message, "❌ No registered numbers")
            return

        # send as text (NO FILE → no error)
        output = "\n".join(result)

        bot.send_message(message.chat.id, f"✅ Registered:\n\n{output}")

    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}")


print("BOT STARTED")
bot.infinity_polling(timeout=60, long_polling_timeout=60)
