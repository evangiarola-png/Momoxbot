import os
import re
import requests
import base64
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

TOKEN = os.environ.get("TELEGRAM_TOKEN")
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_KEY")

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 Analyse...")
    photo = await update.message.photo[-1].get_file()
    data = await photo.download_as_bytearray()
    b64 = base64.b64encode(data).decode()
    r = requests.post("https://api.anthropic.com/v1/messages", json={
        "model": "claude-haiku-4-5-20251001",
        "max_tokens": 50,
        "messages": [{"role": "user", "content": [
            {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": b64}},
            {"type": "text", "text": "ISBN or barcode number only, digits only."}
        ]}]
    }, headers={"x-api-key": ANTHROPIC_KEY, "anthropic-version": "2023-06-01", "content-type": "application/json"})
    isbn = r.json()["content"][0]["text"].strip().replace("-","").replace(" ","")
    url = f"https://www.momox.fr/prix-rachat/?search={isbn}"
    r2 = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    match = re.search(r'"price"\s*:\s*"?([\d,\.]+)"?', r2.text)
    price = match.group(1) + "€" if match else "Prix non trouvé"
    await update.message.reply_text(f"📖 {isbn}\n💶 {price}\n🔗 {url}")

Application.builder().token(TOKEN).build().run_polling(allowed_updates=Update.ALL_TYPES)
