from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from datetime import datetime

BOT_TOKEN = "7921805686:AAH0AJrCC0Dd6Lvb5mc3CXI9dUda_n89Y0Y"

def parse_mrz(mrz1: str, mrz2: str):
    try:
        mrz1 = mrz1.strip().replace('\n', '')
        mrz2 = mrz2.strip().replace('\n', '')

        surname_name_raw = mrz1[5:].split('<<')
        surname = surname_name_raw[0].replace('<', ' ').strip()
        name = surname_name_raw[1].replace('<', ' ').strip()

        passport_number = mrz2[0:9].replace('<', '')
        nationality = mrz2[10:13]
        birth_date_raw = mrz2[13:19]
        sex = mrz2[20]
        expiry_date_raw = mrz2[21:27]

        birth_date = datetime.strptime(birth_date_raw, "%y%m%d").strftime("%d%b%y").upper()
        expiry_date = datetime.strptime(expiry_date_raw, "%y%m%d").strftime("%d%b%y").upper()

        return f"SR DOCS YY HK1-P-{nationality}-{passport_number}-{nationality}-{birth_date}-{sex}-{expiry_date}-{surname.upper()}-{name.upper()}"
    except:
        return "⚠️ Не удалось распознать MRZ. Убедитесь, что ввели ровно 2 строки, как в паспорте."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я помогу тебе сгенерировать строку для Amadeus.\n\n"
        "📸 Просто отправь 2 нижние строки с паспорта (MRZ), например:\n\n"
        "`P<UZBIBRAGIMOVA<<BARNO<BAKTIYAROVNA<<<<<<`\n"
        "`FA0421711<8UZB8611292F2907023<<<<<<<<<<<<<<04`\n\n"
        "И я верну готовую строку, которую можно скопировать.",
        parse_mode="Markdown"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    lines = text.split('\n')

    if len(lines) == 2 and lines[0].startswith('P<'):
        result = parse_mrz(lines[0], lines[1])
        await update.message.reply_text(result)
    else:
        await update.message.reply_text("❗Пожалуйста, отправьте 2 строки MRZ подряд, как на паспорте.")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("🤖 Бот запущен.")
app.run_polling()
