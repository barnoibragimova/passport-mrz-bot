import os
import logging
import pytesseract
from PIL import Image
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Отправь мне фото паспорта, и я распознаю данные.")


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file = await photo.get_file()
    file_path = "passport.jpg"
    await file.download_to_drive(file_path)

    image = Image.open(file_path)
    text = pytesseract.image_to_string(image)

    await update.message.reply_text(f"Распознанный текст:\n\n{text}")


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("Bot started...")
    app.run_polling()


if __name__ == "__main__":
    main()
