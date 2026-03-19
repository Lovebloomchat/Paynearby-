import os
import telebot
from playwright.sync_api import sync_playwright

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise Exception("BOT_TOKEN missing")

bot = telebot.TeleBot(TOKEN)

URL = "https://retailerportal.paynearby.in/auth/login?source=paynearby-site"

# 🔐 TERA LOGIN DATA
LOGIN_NUMBER = "9973028650"
LOGIN_PASSWORD = "Shubham@9282"


def check_numbers(numbers):
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = browser.new_page()

        # 🔥 STEP 1: LOGIN (ONLY ONCE)
        page.goto(URL)

        page.fill("input[type='tel']", LOGIN_NUMBER)
        page.fill("input[type='password']", LOGIN_PASSWORD)
        page.click("button")

        print("LOGIN DONE")

        # ⏱️ short wait
        for _ in range(12):
            page.wait_for_timeout(1000)

        print("START CHECK")

        # 🔁 LOOP
        for num in numbers:
            try:
                page.fill("input[type='tel']", "")
                page.fill("input[type='tel']", num)

                page.wait_for_timeout(1200)

                content = page.content().lower()

                if "not registered" not in content:
                    results.append(num)

            except Exception as e:
                print("ERROR:", e)

        browser.close()

    return results


@bot.message_handler(commands=['start'])
def start(msg):
    bot.reply_to(msg, "Send numbers (one per line)")


# 🔥 DIRECT NUMBER INPUT
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    try:
        bot.reply_to(message, "⏳ Checking...")

        numbers = [x.strip() for x in message.text.split() if x.strip()]

        result = check_numbers(numbers)

        if not result:
            bot.reply_to(message, "❌ No registered numbers")
            return

        output = "\n".join(result)

        bot.send_message(message.chat.id, f"✅ Registered:\n\n{output}")

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")


print("🚀 BOT STARTED")
bot.infinity_polling(timeout=60, long_polling_timeout=60)
