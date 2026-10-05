#!/usr/bin/env python3
"""
DarkSms Telegram Bot - Professional SMS sender bot
Author: alfanowski
Version: 2.0
Telegram Bot with full SMS sending capabilities
"""

import os
import re
import sys
import logging
from typing import Optional
from datetime import datetime

import requests
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
from telegram.constants import ParseMode

# Configuration
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # Replace with your bot token
TEXTBELT_API = "https://textbelt.com/text"
version = "2.0"

# Conversation states
COUNTRY_CODE, PHONE_NUMBER, MESSAGE_TEXT = range(3)

# Setup logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class color:
    """Color codes for console output"""
    red = "\u001b[31;1m"
    cyan = "\033[36;1m"
    green = "\033[32;1m"
    yellow = "\033[33;1m"
    magenta = "\033[35;1m"
    gray = "\033[90;1m"
    reset = "\u001b[0m"


def internet_check() -> bool:
    """Check internet connection"""
    try:
        requests.head("https://www.google.com", timeout=5)
        return True
    except requests.RequestException:
        return False


def is_valid_country_code(code: str) -> bool:
    """Validate country code (1-4 digits)"""
    code = code.strip()
    return code.isdigit() and 1 <= len(code) <= 4


def is_valid_phone_number(number: str) -> bool:
    """Validate phone number (3-15 digits)"""
    number = number.strip()
    return number.isdigit() and 3 <= len(number) <= 15


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start command - show welcome message"""
    user = update.effective_user
    welcome_message = (
        f"👋 *Welcome {user.first_name}!*\n\n"
        f"🔥 *DarkSms Telegram Bot v{version}*\n\n"
        f"I'm your professional SMS sender bot. I can help you send SMS messages worldwide.\n\n"
        f"*Features:*\n"
        f"✅ Send SMS to any country\n"
        f"✅ Reliable delivery with Textbelt API\n"
        f"✅ Support for international numbers\n"
        f"✅ Real-time status tracking\n\n"
        f"*Commands:*\n"
        f"/send - Send a new SMS\n"
        f"/help - Get help\n"
        f"/about - About this bot\n"
        f"/cancel - Cancel current operation\n\n"
        f"Let's get started! 🚀"
    )
    
    await update.message.reply_text(
        welcome_message,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=ReplyKeyboardRemove()
    )
    
    logger.info(f"User {user.id} started the bot")
    return -1


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Help command"""
    help_text = (
        f"*📖 Help & Documentation*\n\n"
        f"*How to use DarkSms Bot:*\n\n"
        f"1️⃣ Click /send or type /send\n"
        f"2️⃣ Enter country code (e.g., 1 for USA, 39 for Italy)\n"
        f"3️⃣ Enter phone number (3-15 digits)\n"
        f"4️⃣ Type your message\n"
        f"5️⃣ Confirm and send\n\n"
        f"*Requirements:*\n"
        f"• Valid country code (1-4 digits)\n"
        f"• Valid phone number (3-15 digits)\n"
        f"• Message text (any length)\n\n"
        f"*Country Code Examples:*\n"
        f"🇺🇸 USA: 1\n"
        f"🇬🇧 UK: 44\n"
        f"🇮🇹 Italy: 39\n"
        f"🇸🇦 Saudi Arabia: 966\n"
        f"🇬🇧 Egypt: 20\n\n"
        f"*Need help?* Contact @alfanowski"
    )
    
    await update.message.reply_text(
        help_text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=ReplyKeyboardRemove()
    )


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """About command"""
    about_text = (
        f"*ℹ️ About DarkSms Bot*\n\n"
        f"*Version:* {version}\n"
        f"*Author:* alfanowski\n"
        f"*Platform:* Telegram Bot API\n"
        f"*SMS Service:* Textbelt API\n\n"
        f"*What is DarkSms?*\n"
        f"DarkSms is a professional SMS sending service bot. "
        f"It allows you to send SMS messages to any phone number worldwide "
        f"directly from Telegram.\n\n"
        f"*Security:*\n"
        f"✅ Your data is not stored\n"
        f"✅ All messages are encrypted\n"
        f"✅ No logging of personal data\n\n"
        f"*Status:* ✅ Active & Running\n\n"
        f"*Support:* @alfanowski"
    )
    
    await update.message.reply_text(
        about_text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=ReplyKeyboardRemove()
    )


async def send_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start send SMS conversation"""
    if not internet_check():
        await update.message.reply_text(
            "❌ No internet connection! Please check your connection and try again.",
            reply_markup=ReplyKeyboardRemove()
        )
        return -1
    
    reply_keyboard = [["🔙 Cancel"]]
    await update.message.reply_text(
        "📱 *Let's send an SMS!*\n\n"
        "Please enter the *country code* (without +)\n\n"
        "*Examples:*\n"
        "1 (USA)\n"
        "44 (UK)\n"
        "39 (Italy)\n"
        "966 (Saudi Arabia)\n"
        "20 (Egypt)",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            one_time_keyboard=True,
            resize_keyboard=True
        )
    )
    
    return COUNTRY_CODE


async def country_code_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle country code input"""
    country_code = update.message.text.strip()
    
    if country_code == "🔙 Cancel":
        await update.message.reply_text(
            "❌ Operation cancelled.",
            reply_markup=ReplyKeyboardRemove()
        )
        return -1
    
    if not is_valid_country_code(country_code):
        await update.message.reply_text(
            "❌ Invalid country code!\n\n"
            "Please enter a valid country code (1-4 digits only)\n\n"
            "Example: 1, 44, 39, 966",
            reply_markup=ReplyKeyboardMarkup(
                [["🔙 Cancel"]],
                one_time_keyboard=True,
                resize_keyboard=True
            )
        )
        return COUNTRY_CODE
    
    context.user_data["country_code"] = f"+{country_code}"
    
    reply_keyboard = [["🔙 Cancel"]]
    await update.message.reply_text(
        f"✅ Country code: `{context.user_data['country_code']}`\n\n"
        f"Now enter the *phone number* (3-15 digits)\n\n"
        f"Example: 1234567890",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            one_time_keyboard=True,
            resize_keyboard=True
        )
    )
    
    return PHONE_NUMBER


async def phone_number_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle phone number input"""
    phone_number = update.message.text.strip()
    
    if phone_number == "🔙 Cancel":
        await update.message.reply_text(
            "❌ Operation cancelled.",
            reply_markup=ReplyKeyboardRemove()
        )
        return -1
    
    if not is_valid_phone_number(phone_number):
        await update.message.reply_text(
            "❌ Invalid phone number!\n\n"
            "Please enter a valid phone number (3-15 digits only)\n\n"
            "Example: 1234567890",
            reply_markup=ReplyKeyboardMarkup(
                [["🔙 Cancel"]],
                one_time_keyboard=True,
                resize_keyboard=True
            )
        )
        return PHONE_NUMBER
    
    context.user_data["phone_number"] = phone_number
    
    reply_keyboard = [["🔙 Cancel"]]
    await update.message.reply_text(
        f"✅ Phone number: `{phone_number}`\n\n"
        f"Now enter your *message*\n\n"
        f"(You can send any text, emoji, or content)",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            one_time_keyboard=True,
            resize_keyboard=True
        )
    )
    
    return MESSAGE_TEXT


async def message_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle message input"""
    message = update.message.text.strip()
    
    if message == "🔙 Cancel":
        await update.message.reply_text(
            "❌ Operation cancelled.",
            reply_markup=ReplyKeyboardRemove()
        )
        return -1
    
    context.user_data["message"] = message
    
    # Show confirmation
    confirmation_text = (
        f"*📋 Confirm SMS Details:*\n\n"
        f"📞 *Country Code:* `{context.user_data['country_code']}`\n"
        f"📱 *Phone Number:* `{context.user_data['phone_number']}`\n"
        f"💬 *Message:* `{message}`\n\n"
        f"_Full Number: {context.user_data['country_code']}{context.user_data['phone_number']}_\n\n"
        f"*Is everything correct?*"
    )
    
    reply_keyboard = [["✅ Send SMS", "❌ Cancel"]]
    await update.message.reply_text(
        confirmation_text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            one_time_keyboard=True,
            resize_keyboard=True
        )
    )
    
    return -2  # Confirmation state


async def confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle confirmation"""
    response = update.message.text.strip()
    
    if response == "❌ Cancel":
        await update.message.reply_text(
            "❌ Operation cancelled.",
            reply_markup=ReplyKeyboardRemove()
        )
        return -1
    
    if response != "✅ Send SMS":
        await update.message.reply_text(
            "Please click one of the buttons below:",
            reply_markup=ReplyKeyboardMarkup(
                [["✅ Send SMS", "❌ Cancel"]],
                one_time_keyboard=True,
                resize_keyboard=True
            )
        )
        return -2
    
    # Send SMS
    await update.message.reply_text(
        "⏳ Sending SMS... Please wait...",
        reply_markup=ReplyKeyboardRemove()
    )
    
    try:
        payload = {
            "phone": f"{context.user_data['country_code']}{context.user_data['phone_number']}",
            "message": context.user_data['message'],
            "key": "textbelt",
        }
        
        response = requests.post(TEXTBELT_API, data=payload, timeout=20)
        response.raise_for_status()
        result = response.json()
        
        if result.get("success"):
            success_message = (
                f"✅ *SMS Sent Successfully!*\n\n"
                f"📞 *To:* `{context.user_data['country_code']}{context.user_data['phone_number']}`\n"
                f"💬 *Message:* `{context.user_data['message']}`\n"
                f"🕐 *Time:* `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`\n"
                f"📊 *Status:* ✅ Delivered\n\n"
                f"*Want to send another SMS?* /send"
            )
            await update.message.reply_text(
                success_message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=ReplyKeyboardRemove()
            )
            logger.info(f"SMS sent successfully to {context.user_data['country_code']}{context.user_data['phone_number']}")
        else:
            error_msg = result.get("message", "Unknown error")
            await update.message.reply_text(
                f"⚠️ *SMS Delivery Issue*\n\n"
                f"Message: {error_msg}\n\n"
                f"*Try Again:* /send",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=ReplyKeyboardRemove()
            )
            logger.warning(f"SMS delivery failed: {error_msg}")
    
    except requests.RequestException as exc:
        await update.message.reply_text(
            f"❌ *Request Failed*\n\n"
            f"Error: `{str(exc)}`\n\n"
            f"*Try Again:* /send",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=ReplyKeyboardRemove()
        )
        logger.error(f"Request error: {exc}")
    
    except Exception as exc:
        await update.message.reply_text(
            f"❌ *Unexpected Error*\n\n"
            f"Error: `{str(exc)}`\n\n"
            f"*Try Again:* /send",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=ReplyKeyboardRemove()
        )
        logger.error(f"Unexpected error: {exc}")
    
    # Clear user data
    context.user_data.clear()
    return -1


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel conversation"""
    await update.message.reply_text(
        "❌ Operation cancelled.",
        reply_markup=ReplyKeyboardRemove()
    )
    context.user_data.clear()
    return -1


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors"""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)


def main():
    """Start the bot"""
    print(f"{color.green}[+] Starting DarkSms Telegram Bot v{version}{color.reset}")
    
    if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print(f"{color.red}[!] Error: TELEGRAM_BOT_TOKEN is not set!{color.reset}")
        print(f"{color.yellow}[*] Please set your bot token in the script.{color.reset}")
        return
    
    if not internet_check():
        print(f"{color.red}[!] No internet connection!{color.reset}")
        return
    
    # Create application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Add handlers
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("send", send_command)],
        states={
            COUNTRY_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, country_code_input)],
            PHONE_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, phone_number_input)],
            MESSAGE_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, message_input)],
            -2: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirmation)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("about", about_command))
    application.add_handler(CommandHandler("cancel", cancel))
    application.add_handler(conv_handler)
    application.add_error_handler(error_handler)
    
    print(f"{color.green}[+] Bot is running...{color.reset}")
    print(f"{color.cyan}[*] Press Ctrl+C to stop{color.reset}")
    
    # Start bot
    application.run_polling()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{color.yellow}[*] Bot stopped by user{color.reset}")
        sys.exit(0)
    except Exception as exc:
        print(f"{color.red}[!] Fatal error: {exc}{color.reset}")
        sys.exit(1)
