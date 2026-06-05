import os
import re
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import base64

TOKEN = os.environ.get("TELEGRAM_TOKEN")

async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 Analyse en cours...")
    photo = await update.message.photo[-1].get_file()
    data = await photo.download_as_bytearray()
    b64 = base64.b64encode(data).decode()
    
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": "claude-opus-4-6",
        "max_tokens": 100,
        "messages": [{"role": "user", "content": [
            {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": b64}},
            {"type": "text", "text": "Extract the ISBN or barcode number from this image. Reply with ONLY the number, nothing else."}
        ]}]
    }
    r = requests.post("https://api.anthropic.com/v1/messages", json=payload, headers=headers)
    isbn = r.json()["content"][0]["text"].strip()
    
    if not isbn.isdigit():
        await update.message.reply_text("❌ Aucun code-barres détecté.")
        return
    
    await update.message.reply_text(f"📖 ISBN: {isbn}\n🔍 Recherche Momox...")
    url = f"https://www.momox.fr/prix-rachat/?search={isbn}"
    headers2 = {"User-Agent": "Mozilla/5.0"}
    r2 = requests.get(url, headers=headers2)
    match = re.search(r'"price"\s*:\s*"?([\d,\.]+)"?', r2.text)
    if match:
        await update.message.reply_text(f"💶 Momox: {match.group(1)} €\n🔗 {url}")
    else:
        await update.message.reply_text(f"😕 Prix non trouvé.\n🔗 {url}")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.PHOTO, handle_image))
app.run_polling()
