import telegram



TELEGRAM_BOT_API_KEY = os.getenv('TELEGRAM_BOT_API_KEY')
chat_id = os.getenv('CHAT_ID')
chat_tag = os.getenv('CHAT_TAG')
bot = telegram.Bot(TELEGRAM_BOT_API_KEY)


# Function to format the message
def format_property_message(row):
    return (
        f"🏠 **{row['title']}**\n"
        f"📍 Location: {row['city']}, {row['neighbourhood']}, {row['road']}\n"
        f"📏 Size: {row['square_meters']} m²\n"
        f"🏢 Floor: {row['floor']}\n"
        f"💰 Price: €{row['price']:,}\n"
        f"🔗 [View Listing]({row['url']})\n"
        "----------------------------------------"
    )


def send_message(message):

    bot.sendMessage(chat_id=chat_id, text=message, parse_mode=telegram.ParseMode.MARKDOWN)

