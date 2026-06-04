import os
import re
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from pyzbar.pyzbar import decode
from PIL import Image
import io

TOKEN = os.environ.get("TELEGRAM_TOKEN")

async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = await update.message.photo[-1].get_file()
    data = await photo.download_as_bytearray()
    img = Image.open(io.BytesIO(data))
    barcodes = decode(img)
    if not barcodes:
        await update.message.reply_text("❌ Aucun code-barres détecté. Reprends la photo de plus près.")
        return
    isbn = barcodes[0].data.decode("utf-8")
    await update.message.reply_text(f"📖 ISBN détecté : {isbn}\n🔍 Recherche sur Momox...")
    url = f"https://www.momox.fr/prix-rachat/?search={isbn}"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    match = re.search(r'"price"\s*:\s*"?([\d,\.]+)"?', r.text)
    if match:
        price = match.group(1)
        await update.message.reply_text(f"💶 Momox rachète ce livre : {price} €\n🔗 {url}")
    else:
        await update.message.reply_text(f"😕 Prix non trouvé automatiquement.\n🔗 Vérifie ici : {url}")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.PHOTO, handle_image))
app.run_polling()
