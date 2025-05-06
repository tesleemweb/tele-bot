import asyncio
import logging
import re
import nest_asyncio
from telethon import TelegramClient, events
import time
import urllib.request

# ===== CONFIG =====
api_id = 20915433
api_hash = '70dc27f0a11c99f909906a40bfae51b9'
bot_token = '7223098306:AAGjuOKhW31grOVqT6Ew5NMaIvutjDDRrF8'  # Replace with your actual bot token
session_name = 'forwarder_session'
source_chat = 'https://t.me/signal341'
target_chat = 'https://t.me/redox12'

# ===== SETUP =====
nest_asyncio.apply()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S"
)

client = TelegramClient(session_name, api_id, api_hash)

# ===== CAPTION PARSER =====
def parse_caption(text):
    text = text.strip()
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    lower = text.lower()

    # ARI Wallet
    ari = re.search(r"(ari wallet\s*\|\s*quiz\s*:\s*\d{1,2} \w+)", text, re.IGNORECASE)
    if ari:
        return ari.group(1).strip()

    # XENEA Quiz
    if "xenea" in lower and "quiz" in lower:
        header = next((l for l in lines if 'xenea' in l.lower()), "")
        date_line = next((l for l in lines if 'quiz' in l.lower()), "")
        return "\n".join(filter(None, [header, date_line])) or "XENEA QUIZ"

    return None

# ===== MESSAGE HANDLER =====
@client.on(events.NewMessage(chats=source_chat))
async def handler(event):
    try:
        if not getattr(event, 'photo', None):
            logging.info("Skipped: No photo in message.")
            return

        caption = parse_caption(event.raw_text or "")
        if caption:
            await client.send_file(target_chat, event.photo, caption=caption)
            logging.info(f"Forwarded with caption:\n{caption}")
        else:
            logging.info("Skipped: No matching caption keyword.")
    except Exception as e:
        logging.error(f"Error forwarding message: {e}")

# ===== CONNECTIVITY CHECK =====
def is_connected():
    try:
        urllib.request.urlopen('https://www.google.com', timeout=5)
        return True
    except:
        return False

# ===== MAIN FUNCTION =====
async def main():
    await client.start(bot_token=bot_token)  # Start the bot using the bot token directly
    logging.info("Bot is online and listening for messages.")
    await client.run_until_disconnected()

# ===== MAIN RUNNER LOOP =====
def run_bot_forever():
    while True:
        try:
            if not is_connected():
                logging.warning("No internet connection. Retrying in 30 seconds...")
                time.sleep(30)
                continue

            asyncio.run(main())
        except Exception as e:
            logging.exception(f"Bot crashed: {e}")
            logging.info("Restarting in 1 minute...")
            time.sleep(60)

# ===== ENTRY POINT =====
if __name__ == '__main__':
    run_bot_forever()
