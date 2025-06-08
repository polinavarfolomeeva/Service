from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from loguru import logger
import math

from app.keyboards.keyboards import (
    get_main_menu, get_products_keyboard, get_services_keyboard, 
    get_product_detail_keyboard, get_service_detail_keyboard, 
    get_categories_keyboard
)
from app.services.api_service import api_service
from app.utils.formatting import format_message, format_product_info, format_service_info

router = Router()

@router.callback_query(F.data == "order_history")
async def order_history_handler(callback: CallbackQuery):
    logger.info("Обработчик 'order_history' вызван!")

    phone_number = "79991234567"

    try:
        response = await api_service.get_purchase_history_by_phone(phone_number)

        if response["status"] != 200:
            await callback.message.answer("Не удалось получить историю заказов.")
            await callback.answer()
            return

        orders = response["data"].get("orders", [])

        if not orders:
            await callback.message.answer("📭 У вас пока нет заказов.")
            await callback.answer()
            return

        history_text = "<b>📦 История заказов</b>\n\n"

        for i, order in enumerate(orders, start=1):
            history_text += (
                f"{bold(f'Заказ №{i}')}\n"
                f"- Дата: {order.get('Дата', '—')}\n"
                f"- Статус: {order.get('Статус', '—')}\n"
                f"- Сумма: {order.get('Сумма', '—')} руб.\n"
                f"- Товары:\n"
            )
            товары = order.get("Товары", [])
            for j, item in enumerate(товары, start=1):
                history_text += (
                    f"  {j}. {item.get('Наименование', '—')} — {item.get('Количество', 1)} шт × {item.get('Цена', '—')} руб.\n"
                )
            history_text += "\n"

        if callback.message.text:
            await callback.message.edit_text(
                text=history_text,
                reply_markup=get_back_to_profile_keyboard(),
                parse_mode="HTML"
            )
        else:
            await callback.message.answer(
                text=history_text,
                reply_markup=get_back_to_profile_keyboard(),
                parse_mode="HTML"
            )

    except Exception as e:
        logger.error(f"Ошибка при получении истории заказов: {e}")
        await callback.message.answer("Произошла ошибка при получении истории заказов.")

    await callback.answer()

def get_back_to_profile_keyboard():
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main"),
        width=1
    )
    return builder.as_markup()

@router.callback_query(F.data == "back_to_main")
async def process_back_to_main(callback: CallbackQuery):

    user_name = callback.from_user.first_name
    greeting_text = get_main_menu_text(user_name)

    await callback.message.edit_text(
        greeting_text, 
        reply_markup=get_main_menu(),
        parse_mode="HTML"
    )
    await callback.answer()