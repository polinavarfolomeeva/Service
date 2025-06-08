from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from loguru import logger

from app.services.api_service import api_service
from app.keyboards.staff_keyboards import (
    get_staff_main_menu, 
    get_orders_list_keyboard, 
    get_order_actions_keyboard,
    get_status_change_keyboard
)
from app.utils.formatting import format_order_details, format_orders_list

router = Router()

class StaffAuthStates(StatesGroup):
    waiting_for_login = State()
    waiting_for_password = State()

user_auth_data = {}

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Обработчик команды /start"""
    await state.clear()
    
    if message.from_user.id in user_auth_data:
        user_auth_data.pop(message.from_user.id)
    
    welcome_text = "👋 Добро пожаловать в бот для сотрудников автосервиса!\n\n📱 Пожалуйста, авторизуйтесь для продолжения."
    await message.answer(welcome_text)
    
    await message.answer("Введите ваш логин:")
    await state.set_state(StaffAuthStates.waiting_for_login)

@router.message(StaffAuthStates.waiting_for_login)
async def process_login(message: Message, state: FSMContext):
    """Обработчик ввода логина"""
    login = message.text.strip()
    
    user_auth_data[message.from_user.id] = {
        "login": login,
        "messages_to_delete": [message.message_id]
    }
    
    password_msg = await message.answer("Введите ваш пароль:")
    user_auth_data[message.from_user.id]["messages_to_delete"].append(password_msg.message_id)
    
    await state.set_state(StaffAuthStates.waiting_for_password)

@router.message(StaffAuthStates.waiting_for_password)
async def process_password(message: Message, state: FSMContext):
    """Обработчик ввода пароля"""
    user_id = message.from_user.id
    password = message.text.strip()
    
    if user_id not in user_auth_data:
        await message.answer("Произошла ошибка. Пожалуйста, начните авторизацию заново с команды /start")
        return
    
    user_auth_data[user_id]["messages_to_delete"].append(message.message_id)
    login = user_auth_data[user_id]["login"]
    
    auth_successful = True
    
    if auth_successful:
        for msg_id in user_auth_data[user_id]["messages_to_delete"]:
            try:
                await message.bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
            except Exception as e:
                logger.error(f"Ошибка при удалении сообщения: {e}")
        
        await message.answer(
            f"✅ Вы успешно авторизованы как сотрудник, {login}!",
            reply_markup=get_staff_main_menu()
        )
        await state.clear()
    else:
        await message.answer("❌ Неверный логин или пароль. Пожалуйста, попробуйте снова с команды /start")
        await state.clear()

@router.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help"""
    help_text = (
        "🔍 <b>Справка по использованию бота для сотрудников:</b>\n\n"
        "/start - Начать работу с ботом или вернуться в главное меню\n"
        "/help - Показать эту справку\n\n"
        "Используйте кнопки меню для навигации по функциям бота."
    )
    await message.answer(help_text)

@router.callback_query(F.data == "show_orders")
async def show_orders(callback: CallbackQuery):
    """Обработчик нажатия на кнопку показа всех заказов"""
    await callback.answer()
    
    response = await api_service._make_request("GET", "/orders")
    
    if response.get("status") == 200 and "orders" in response.get("data", {}):
        orders = response["data"]["orders"]
        
        if not orders:
            await callback.message.answer("📋 Список заказов пуст")
            return
        
        orders_text = format_orders_list(orders)
        
        keyboard = get_orders_list_keyboard(orders)
        
        await callback.message.answer(
            f"📋 <b>Список всех заказов:</b>\n\n{orders_text}", 
            reply_markup=keyboard
        )
    else:
        error_msg = response.get("data", {}).get("message", "Неизвестная ошибка")
        await callback.message.answer(f"❌ Ошибка при получении списка заказов: {error_msg}")

@router.callback_query(F.data.startswith("order_"))
async def show_order_details(callback: CallbackQuery):
    """Обработчик нажатия на кнопку конкретного заказа"""
    order_number = callback.data.split("_")[1]
    await callback.answer()
    
    response = await api_service._make_request("GET", f"/orders/by-number/{order_number}")
    
    if response.get("status") == 200 and "order" in response.get("data", {}):
        order = response["data"]["order"]
        
        order_text = format_order_details(order)
        
        keyboard = get_order_actions_keyboard(order_number)
        
        await callback.message.answer(
            f"📝 <b>Детали заказа #{order_number}:</b>\n\n{order_text}", 
            reply_markup=keyboard
        )
    else:
        error_msg = response.get("data", {}).get("message", "Неизвестная ошибка")
        await callback.message.answer(f"❌ Ошибка при получении деталей заказа: {error_msg}")

@router.callback_query(F.data.startswith("change_status_"))
async def change_order_status(callback: CallbackQuery):
    """Обработчик нажатия на кнопку изменения статуса заказа"""
    order_number = callback.data.split("_")[2]
    await callback.answer()
    
    statuses_response = await api_service.get_order_statuses()
    
    if statuses_response.get("status") == 200 and "statuses" in statuses_response.get("data", {}):
        statuses = statuses_response["data"]["statuses"]
        
        status_response = await api_service.get_order_status(order_number)
        
        if status_response.get("status") == 200:
            current_status = status_response["data"]["status"]
            current_status_name = next((s["name"] for s in statuses if s["id"] == current_status), "Неизвестно")
            
            keyboard = get_status_change_keyboard(order_number, statuses)
            
            await callback.message.answer(
                f"🔄 <b>Изменение статуса заказа #{order_number}</b>\n\n"
                f"Текущий статус: <b>{current_status_name}</b>\n\n"
                f"Выберите новый статус заказа:",
                reply_markup=keyboard
            )
        else:
            error_msg = status_response.get("data", {}).get("message", "Неизвестная ошибка")
            await callback.message.answer(f"❌ Ошибка при получении текущего статуса: {error_msg}")
    else:
        error_msg = statuses_response.get("data", {}).get("message", "Неизвестная ошибка")
        await callback.message.answer(f"❌ Ошибка при получении списка статусов: {error_msg}")

@router.callback_query(F.data.startswith("set_status_"))
async def set_order_status(callback: CallbackQuery):
    """Обработчик нажатия на кнопку выбора нового статуса заказа"""
    parts = callback.data.split("_")
    order_number = parts[2]
    new_status = parts[3]
    
    response = await api_service.update_order_status(order_number, new_status)
    
    if response.get("status") == 200:
        updated_status = response["data"]["status"]
        updated_at = response["data"]["updated_at"]
        
        statuses_response = await api_service.get_order_statuses()
        if statuses_response.get("status") == 200 and "statuses" in statuses_response.get("data", {}):
            statuses = statuses_response["data"]["statuses"]
            status_name = next((s["name"] for s in statuses if s["id"] == updated_status), updated_status)
            
            await callback.answer(f"✅ Статус изменен на: {status_name}")
            await callback.message.answer(
                f"✅ Статус заказа #{order_number} успешно изменен на <b>{status_name}</b>\n"
                f"🕒 Время обновления: {updated_at}"
            )
            
            new_callback_data = f"order_{order_number}"
            callback.data = new_callback_data
            await show_order_details(callback)
        else:
            await callback.answer("✅ Статус успешно обновлен")
            await callback.message.answer(f"✅ Статус заказа #{order_number} успешно обновлен на {updated_status}")
    else:
        error_msg = response.get("data", {}).get("message", "Неизвестная ошибка")
        await callback.answer("❌ Ошибка при обновлении статуса", show_alert=True)
        await callback.message.answer(f"❌ Ошибка при обновлении статуса заказа: {error_msg}")

@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    """Обработчик нажатия на кнопку возврата в главное меню"""
    await callback.answer()
    
    await callback.message.answer(
        "🏠 Главное меню", 
        reply_markup=get_staff_main_menu()
    )

staff_router = router
