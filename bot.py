import logging
import easyocr
from PIL import Image
import numpy as np
import cv2
from io import BytesIO
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Токен твоего бота
TOKEN = "7921805686:AAH0AJrCC0Dd6Lvb5mc3CXI9dUda_n89Y0Y"

# EasyOCR reader
reader = easyocr.Reader(["en"])

# Функция для извлечения MRZ-зоны
def extract_mrz_text(image):
    img_array = np.array(image)
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    results = reader.readtext(gray)
    mrz_lines = []

    for result in results:
        text = result[1]
        if len(text) > 30 and all(char.isupper() or char.isdigit() or char in "<>" for char in text):
            mrz_lines.append(text.strip())

    if len(mrz_lines) >= 2:
        return "\n".join(mrz_lines[-2:])
    elif mrz_lines:
        return mrz_lines[-1]
    else:
        return "MRZ-зона не найдена. Попробуйте загрузить фото крупнее и четче."

# Асинхронная функция для обработки сообщений с фото
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    photo_file = await update.message.photo[-1].get_file()
    photo_bytes = await photo_file.download_as_bytearray()
    image = Image.open(BytesIO(photo_bytes))

    mrz_text = extract_mrz_text(image)

    await update.message.reply_text(f"Распознанный MRZ:\n{mrz_text}")

# Основная функция запуска бота
async def main():
    app = Application.builder().token(TOKEN).build()

    # Обработка фото
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    # Запуск бота
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
