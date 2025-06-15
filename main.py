import re
import logging
import pytesseract
import cv2
import numpy as np
from io import BytesIO
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from PIL import Image

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Шаблон для поиска паспортных данных
PASSPORT_PATTERN = re.compile(
    r'([A-Z0-9<]+)\s+([A-Z0-9<]+)\s+([A-Z0-9<]+)\s+([A-Z0-9<]+)\s+([A-Z]{3})\s+(\d{2}[A-Z]{3}\d{2})\s+([FM])\s+(\d{2}[A-Z]{3}\d{2})\s+([A-Z<]+)\s+([A-Z<]+)',
    re.IGNORECASE
)

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_markdown_v2(
        "📄 *Привет\!* Отправьте мне *фото последних двух строк паспорта*, и я преобразую их в формат AMADEUS\.\n\n"
        "Пример данных, которые я ищу:\n"
        "```\n"
        "P<UZBFA0421711<1111111M1111111<<<<<<<<<<<<<<<0\n"
        "IBRAGIMOVA<<BARNO<BAKTIYAROVNA<<<<<<<<<<<<<<\n"
        "```\n\n"
        "Я верну формат:\n"
        "`SR DOCS YY HK1-P-UZB-FA0421711-UZB-29NOV86-F-02JUL29-IBRAGIMOVA-BARNO BAKTIYAROVNA`"
    )

def extract_text_from_image(image_bytes):
    """Извлекает текст с изображения с помощью Tesseract OCR."""
    try:
        # Преобразуем в OpenCV-формат (numpy array)
        image = Image.open(BytesIO(image_bytes))
        img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Улучшаем контраст для лучшего распознавания
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
        
        # Распознаем текст
        text = pytesseract.image_to_string(thresh, config='--psm 6')
        return text.strip()
    except Exception as e:
        logger.error(f"OCR Error: {e}")
        return None

def process_passport_photo(update: Update, context: CallbackContext) -> None:
    if not update.message.photo:
        update.message.reply_text("Пожалуйста, отправьте фото паспорта.")
        return
    
    # Берем самое большое изображение (лучшее качество)
    photo_file = update.message.photo[-1].get_file()
    image_bytes = BytesIO()
    photo_file.download(out=image_bytes)
    image_bytes.seek(0)
    
    # Извлекаем текст
    extracted_text = extract_text_from_image(image_bytes.read())
    if not extracted_text:
        update.message.reply_text("❌ Не удалось прочитать текст. Попробуйте отправить более четкое фото.")
        return
    
    logger.info(f"Extracted text: {extracted_text}")
    
    # Ищем паспортные данные
    match = PASSPORT_PATTERN.search(extracted_text)
    if not match:
        update.message.reply_text(
            "❌ Не удалось распознать паспортные данные. Убедитесь, что фото содержит последние две строки паспорта.\n\n"
            "Пример правильного формата:\n"
            "```\n"
            "P<UZBFA0421711<1111111M1111111<<<<<<<<<<<<<<<0\n"
            "IBRAGIMOVA<<BARNO<BAKTIYAROVNA<<<<<<<<<<<<<<\n"
            "```"
        )
        return
    
    # Форматируем в AMADEUS
    try:
        doc_type = match.group(1)  # P
        country = match.group(2)   # UZB
        passport_number = match.group(3)  # FA0421711
        birth_date = match.group(6)  # 29NOV86
        gender = match.group(7)  # F/M
        expiry_date = match.group(8)  # 02JUL29
        last_name = match.group(9).replace('<', '')  # IBRAGIMOVA
        first_name = match.group(10).replace('<', ' ').strip()  # BARNO BAKTIYAROVNA
        
        amadeus_format = f"SR DOCS YY HK1-P-{country}-{passport_number}-{country}-{birth_date}-{gender}-{expiry_date}-{last_name}-{first_name}"
        
        update.message.reply_text(
            f"✅ Формат AMADEUS:\n\n`{amadeus_format}`\n\nСкопируйте текст.",
            parse_mode='MarkdownV2'
        )
    except Exception as e:
        logger.error(f"Error parsing passport: {e}")
        update.message.reply_text("❌ Ошибка при обработке данных. Попробуйте другое фото.")

def error_handler(update: Update, context: CallbackContext):
    logger.error("Exception:", exc_info=context.error)
    if update.message:
        update.message.reply_text("⚠️ Произошла ошибка. Попробуйте позже.")

def main():
    updater = Updater("7921805686:AAH0AJrCC0Dd6Lvb5mc3CXI9dUda_n89Y0Y", use_context=True)
    dispatcher = updater.dispatcher
    
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.photo, process_passport_photo))
    dispatcher.add_error_handler(error_handler)
    
    updater.start_polling()
    logger.info("Бот запущен и ждет фото паспортов...")
    updater.idle()

if __name__ == '__main__':
    main()
