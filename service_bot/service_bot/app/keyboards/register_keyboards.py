from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

def get_contact_keyboard() -> ReplyKeyboardMarkup:

    builder = ReplyKeyboardBuilder()

    builder.row(
        KeyboardButton(text="📱 Поделиться контактом", request_contact=True),
        width=1
    )

    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)

def get_login_choice_keyboard() -> InlineKeyboardMarkup:

    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="✅ Использовать email как логин", callback_data="use_email_as_login"),
        width=1
    )

    builder.row(
        InlineKeyboardButton(text="🔄 Ввести другой логин", callback_data="manual_login"),
        width=1
    )

    builder.row(
        InlineKeyboardButton(text="❌ Отмена", callback_data="cancel"),
        width=1
    )

    return builder.as_markup()
