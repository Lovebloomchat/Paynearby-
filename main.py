import os
import telebot
from playwright.sync_api import sync_playwright

# 🔐 Token from Railway variable
TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

URL = "https://retailerportal.paynearby.in/auth/login?source=paynearby-site"

def process_numbers(numbers):
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # 🔥 STEP 1: OPEN + LOGIN (ONLY ONCE)
        page.goto(URL)

        page.fill("input[type='tel']", "9999999999")
        page.fill("input[type='password']", "test123")
        page.click("button")

        # ⏱️ FIRST WAIT (IMPORTANT)
        page.wait_for_timeout(40000)

        # 🔁 STEP 2: LOOP (NO REFRESH)
        for num in numbers:
            try:
                page.fill("input[type='tel']", "")
                page.fill("input[type='tel']", num)

                page.wait_for_timeout(1500)

                content = page.content().lower()

                if "not registered" in content:
                    results.append(f"{num},Not Registered")
                else:
                    results.append(f"{num},Registered")

            except:
                results.append(f"{num},Error")

        browser.close()

    return results


@bot.message_handler(commands=['start'])
def start(msg):
    bot.reply_to(msg, "📂 Send .txt file with numbers")


@bot.message_handler(content_types=['document'])
def handle_file(message):
    try:
        file_info = bot.get_file(message.document.file_id)
        file = bot.download_file(file_info.file_path)

        with open("numbers.txt", "wb") as f:
            f.write(file)

        with open("numbers.txt") as f:
            numbers = [line.strip() for line in f if line.strip()]

        bot.reply_to(message, f"🚀 Processing {len(numbers)} numbers...")

        result = process_numbers(numbers)

        with open("result.txt", "w") as f:
            f.write("\n".join(result))

        bot.send_document(message.chat.id, open("result.txt", "rb"))

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")


bot.polling()
