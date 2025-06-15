import re
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Шаблон для чтения паспортных данных
PASSPORT_PATTERN = re.compile(
    r'([A-Z0-9<]+)\s+([A-Z0-9<]+)\s+([A-Z0-9<]+)\s+([A-Z0-9<]+)\s+([A-Z]{3})\s+(\d{2}[A-Z]{3}\d{2})\s+([FM])\s+(\d{2}[A-Z]{3}\d{2})\s+([A-Z<]+)\s+([A-Z<]+)',
    re.IGNORECASE
)

def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Привет, {user.mention_markdown_v2()}\! Отправьте мне последние две строки паспорта, и я преобразую их в формат AMADEUS\.'
        '\n\nПример данных паспорта:'
        '\n```'
        '\nP<UZBFA0421711<1111111M1111111<<<<<<<<<<<<<<<0'
        '\nIBRAGIMOVA<<BARNO<BAKTIYAROVNA<<<<<<<<<<<<<<'
        '\n```'
        '\n\nЯ верну формат:'
        '\n`SR DOCS YY HK1-P-UZB-FA0421711-UZB-29NOV86-F-02JUL29-IBRAGIMOVA-BARNO BAKTIYAROVNA`'
    )

def process_passport(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    
    # Удаляем лишние пробелы и преобразуем в единый формат
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    if len(lines) < 2:
        update.message.reply_text('Пожалуйста, отправьте ДВЕ строки паспортных данных.')
        return
    
    # Объединяем две строки для обработки
    combined = ' '.join(lines[:2])
    match = PASSPORT_PATTERN.match(combined)
    
    if not match:
        update.message.reply_text(
            'Не удалось распознать паспортные данные. Пожалуйста, отправьте последние две строки паспорта.\n\n'
            'Пример правильного формата:\n'
            'P<UZBFA0421711<1111111M1111111<<<<<<<<<<<<<<<0\n'
            'IBRAGIMOVA<<BARNO<BAKTIYAROVNA<<<<<<<<<<<<<<'
        )
        return
    
    try:
        # Извлекаем данные
        doc_type = match.group(1)  # P
        country = match.group(2)   # UZB
        passport_number = match.group(3)  # FA0421711
        birth_date = match.group(6)  # 29NOV86
        gender = match.group(7)  # F/M
        expiry_date = match.group(8)  # 02JUL29
        last_name = match.group(9).replace('<', '')  # IBRAGIMOVA
        first_name = match.group(10).replace('<', ' ').strip()  # BARNO BAKTIYAROVNA
        
        # Форматируем в AMADEUS
        amadeus_format = f"SR DOCS YY HK1-P-{country}-{passport_number}-{country}-{birth_date}-{gender}-{expiry_date}-{last_name}-{first_name}"
        
        # Отправляем результат с возможностью копирования
        update.message.reply_text(
            f"Формат AMADEUS:\n\n`{amadeus_format}`\n\nВы можете скопировать текст.",
            parse_mode='MarkdownV2'
        )
    except Exception as e:
        logger.error(f"Error processing passport: {e}")
        update.message.reply_text('Произошла ошибка при обработке данных. Пожалуйста, проверьте формат и попробуйте снова.')

def error_handler(update: Update, context: CallbackContext):
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    if update and update.message:
        update.message.reply_text('Произошла ошибка. Пожалуйста, попробуйте позже.')

def main():
    # Используем токен, который вы получили от BotFather
    updater = Updater("7921805686:AAH0AJrCC0Dd6Lvb5mc3CXI9dUda_n89Y0Y", use_context=True)
    
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, process_passport))
    dispatcher.add_error_handler(error_handler)
    
    updater.start_polling()
    logger.info("Bot started polling...")
    updater.idle()

if __name__ == '__main__':
    main()
