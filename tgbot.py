import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters, 
    ConversationHandler, CallbackQueryHandler, CallbackContext
)
import gspread
from google.oauth2.service_account import Credentials

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Google Sheets setup
scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file('telegrambot.json', scopes=scopes)
client = gspread.authorize(creds)
sheet = client.open("KeftaTelegrambot").sheet1

# Telegram Bot Token
TOKEN = '6776764805:AAHYBhmXIjqP-ixR_20K8cKEvwqjFjgMXFg'

# States for conversation
NAME, GENDER, EDUCATION, AGE, EMPLOYMENT, REGION = range(6)

# Inline keyboard options
EDUCATION_LEVELS = [
    ["High School", "High School Diploma"],
    ["TVET", "University Degree"],
    ["Masters", "PhD"]
]

AGE_RANGES = [
    ["18-24", "25-34"],
    ["35-44", "45-54"],
    ["55-64", "65+"]
]

EMPLOYMENT_STATUSES = [
    ["Unemployed", "Employed"],
    ["Self-employed", "Student"],
    ["Retired", "Other"]
]

REGIONS = [
    ["Addis Ababa", "Oromia Region"],
    ["Amhara Region", "Tigray Region"],
    ["Afar Region", "Benishangul-Gumuz Region"],
    ["Central Ethiopia Regional State", "Dire Dawa"],
    ["Gambela Region", "Harari Region"],
    ["Sidama Region", "Somali Region"],
    ["South Ethiopia Regional State", "South West Ethiopia Peoples' Region"]
]

async def start(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text('Welcome to the survey! What is your name?')
    return NAME

async def name(update: Update, context: CallbackContext) -> int:
    user_name = update.message.text
    context.user_data['name'] = user_name
    keyboard = [
        [InlineKeyboardButton("Male", callback_data='Male'),
         InlineKeyboardButton("Female", callback_data='Female')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Please choose your gender:', reply_markup=reply_markup)
    return GENDER

async def gender(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data['gender'] = query.data
    keyboard = [[InlineKeyboardButton(text, callback_data=text) for text in pair] for pair in AGE_RANGES]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text('Please select your age range:', reply_markup=reply_markup)
    return AGE

async def age(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data['age'] = query.data
    keyboard = [[InlineKeyboardButton(text, callback_data=text) for text in pair] for pair in EDUCATION_LEVELS]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text('Please select your highest level of education:', reply_markup=reply_markup)
    return EDUCATION

async def education(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data['education'] = query.data
    keyboard = [[InlineKeyboardButton(text, callback_data=text) for text in pair] for pair in EMPLOYMENT_STATUSES]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text('Please select your employment status:', reply_markup=reply_markup)
    return EMPLOYMENT

async def employment(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data['employment'] = query.data
    keyboard = [[InlineKeyboardButton(text, callback_data=text) for text in pair] for pair in REGIONS]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text('Please select your region:', reply_markup=reply_markup)
    return REGION

async def region(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data['region'] = query.data
    # No need to await here since we are calling the function directly
    return await submit_data(update, context)

async def submit_data(update: Update, context: CallbackContext) -> int:
    user_data = context.user_data
    row = [
        user_data.get('name', ''),
        user_data.get('gender', ''),
        user_data.get('age', ''),
        user_data.get('education', ''),
        user_data.get('employment', ''),
        user_data.get('region', '')
    ]
    # Append the row to the Google Sheet
    sheet.append_row(row)
    # Make sure to send the thank you message to the correct chat
    chat_id = update.effective_chat.id
    await context.bot.send_message(chat_id=chat_id, text='Thank you for participating in the survey!')
    return ConversationHandler.END

async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text('The survey has been cancelled.')
    return ConversationHandler.END

def main() -> None:
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name)],
            GENDER: [CallbackQueryHandler(gender)],
            AGE: [CallbackQueryHandler(age)],
            EDUCATION: [CallbackQueryHandler(education)],
            EMPLOYMENT: [CallbackQueryHandler(employment)],
            REGION: [CallbackQueryHandler(region)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(conv_handler)

    application.run_polling()

if __name__ == '__main__':
    main()
