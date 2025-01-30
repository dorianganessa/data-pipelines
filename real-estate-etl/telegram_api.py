import telegram
import os

from dotenv import load_dotenv

load_dotenv()

telegram_bot_api_key = os.getenv('telegram_bot_api_key')
chat_id = os.getenv('chat_id')
chat_tag = os.getenv('chat_tag')

bot = telegram.Bot(telegram_bot_api_key)


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

