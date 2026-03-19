import os
import telebot
from playwright.sync_api import sync_playwright

# 🔐 TOKEN (Railway variable)
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise Exception("❌ BOT_TOKEN not found")

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

        print("LOGIN CLICKED")

        # ⏱️ SMART WAIT (max 40 sec)
        for i in range(40):
            content = page.content().lower()
            if "password" in content:
                print("LOGIN READY")
                break
            page.wait_for_timeout(1000)

        print("START LOOP")

        # 🔁 LOOP (NO REFRESH)
        for num in numbers:
            try:
                page.fill("input[type='tel']", "")
                page.fill("input[type='tel']", num)

                page.wait_for_timeout(1500)

                content = page.content().lower()

                clean_num = num.split(":")[0].replace("+91", "").strip()

                if "not registered" not in content:
                    results.append(clean_num)

            except Exception as e:
                print("ERROR:", e)

        browser.close()

    print("PROCESS DONE")
    return results


@bot.message_handler(commands=['start'])
def start(msg):
    bot.reply_to(msg, "📂 Send .txt file with numbers")


@bot.message_handler(content_types=['document'])
def handle_file(message):
    try:
        bot.reply_to(message, "⏳ Processing started...")

        file_info = bot.get_file(message.document.file_id)
        file = bot.download_file(file_info.file_path)

        with open("numbers.txt", "wb") as f:
            f.write(file)

        with open("numbers.txt") as f:
            numbers = [line.strip() for line in f if line.strip()]

        print("TOTAL NUMBERS:", len(numbers))

        result = process_numbers(numbers)

        # ❗ empty check
        if not result:
            bot.reply_to(message, "❌ No registered numbers found")
            return

        # write result
        with open("result.txt", "w") as f:
            f.write("\n".join(result))

        # ❗ file empty check
        if os.path.getsize("result.txt") == 0:
            bot.reply_to(message, "❌ File empty")
            return

        # ✅ SAFE SEND
        with open("result.txt", "rb") as f:
            bot.send_document(
                message.chat.id,
                f,
                visible_file_name="result.txt"
            )

        bot.reply_to(message, "✅ Done")

    except Exception as e:
        print("MAIN ERROR:", e)
        bot.reply_to(message, f"❌ Error: {str(e)}")


print("🚀 BOT STARTED")
bot.polling()
