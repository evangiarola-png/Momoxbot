import os
import re
import requests
import base64
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

TOKEN = os.environ.get("TELEGRAM_TOKEN")

async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 Analyse en cours...")
    photo = await update.message.photo[-1].get_file()
    data = await photo.download_as_bytearray()
    b64 = base64.b64encode(data).decode()
    headers = {
        "x-api-key": os.environ.get("ANTHROPIC_KEY"),
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    payload = {
        "model": "claude-haiku-4-5-20251001",
        "max_tokens": 50,
        "messages": [{"role": "user", "content": [
            {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": b64}},
            {"type": "text", "text": "What is the ISBN or barcode number? Reply ONLY with the digits."}
        ]}]
    }
    r = requests.post("https://api.anthropic.com/v1/messages", json=payload, headers=headers)
    isbn = r.json()["content"][0]["text"].strip().replace("-","").replace(" ","")
    url = f"https://www.momox.fr/prix-rachat/?search={isbn}"
    r2 = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    match = re.search(r'"price"\s*:\s*"?([\d,\.]+)"?', r2.text)
    price = match.group(1) + " €" if match else "Prix non trouvé"
    await update.message.reply_text(f"📖 ISBN: {isbn}\n💶 Momox: {price}\n🔗 {url}")

Application.builder().token(TOKEN).build().run_polling(allowed_updates=Update.ALL_TYPES)
