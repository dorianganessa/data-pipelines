import telegram
import os
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_API_KEY: str = os.getenv("telegram_bot_api_key")

if TELEGRAM_BOT_API_KEY is None:
    raise ValueError("TELEGRAM_BOT_API_KEY is not set. Please check your environment variables.")

bot: telegram.Bot = telegram.Bot(TELEGRAM_BOT_API_KEY)

chat_id = os.getenv('chat_id')
chat_tag = os.getenv('chat_tag')



# Function to format the message
def format_property_message(row: Dict[str, Any]) -> str:
    """Format a property message for sending via Telegram."""
    return (
        f"🏠 **{row['title']}**\n"
        f"📍 Location: {row['city']}, {row['neighbourhood']}, {row['road']}\n"
        f"📏 Size: {row['square_meters']} m²\n"
        f"🏢 Floor: {row['floor']}\n"
        f"💰 Price: €{row['price']:,}\n"
        f"🔗 [View Listing]({row['url']})\n"
        "----------------------------------------"
    )


def send_message(message: str) -> None:
    """Send a message using the Telegram bot."""
    if chat_id is None:
        raise ValueError("TELEGRAM_CHAT_ID is not set. Please check your environment variables.")
    bot.sendMessage(chat_id=chat_id, text=message, parse_mode=telegram.ParseMode.MARKDOWN)

