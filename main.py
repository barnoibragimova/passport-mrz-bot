import logging
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters
import pytesseract
from PIL import Image
import tempfile

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Отправь фото паспорта, и я сформирую строку для Amadeus.")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = await update.message.photo[-1].get_file()
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
        await photo.download_to_drive(f.name)
        image = Image.open(f.name)
        text = pytesseract.image_to_string(image)
        lines = [line for line in text.splitlines() if len(line) > 40]
        if len(lines) >= 2:
            mrz = lines[-2] + lines[-1]
            await update.message.reply_text(f"Распознано:\n{mrz}")
        else:
            await update.message.reply_text("Не удалось распознать MRZ. Попробуй другое фото.")

def main():
    token = os.environ.get("BOT_TOKEN")
    if not token:
        logger.error("BOT_TOKEN не установлен")
        return

    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    logger.info("Bot started")
    app.run_polling()

if __name__ == "__main__":
    main()
