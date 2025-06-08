from aiogram.types import (
    InlineKeyboardMarkup, 
    InlineKeyboardButton, 
    ReplyKeyboardMarkup, 
    KeyboardButton
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_staff_main_menu() -> InlineKeyboardMarkup:
    """Клавиатура главного меню для бота сотрудников"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="📋 Показать все заказы", callback_data="show_orders")
    )
    builder.row(
        InlineKeyboardButton(text="ℹ️ Помощь", callback_data="help")
    )
    
    return builder.as_markup()

def get_orders_list_keyboard(orders: list) -> InlineKeyboardMarkup:
    """Клавиатура со списком заказов"""
    builder = InlineKeyboardBuilder()
    
    for order in orders:
        order_number = order.get("number")
        client_name = order.get("client", {}).get("name", "Клиент")
        amount = order.get("amount", 0)
        status = order.get("status", "")
        
        button_text = f"№{order_number} - {client_name} - {amount} руб. ({status})"
        builder.row(
            InlineKeyboardButton(
                text=button_text,
                callback_data=f"order_{order_number}"
            )
        )
    
    builder.row(
        InlineKeyboardButton(text="🔙 Назад в меню", callback_data="back_to_menu")
    )
    
    return builder.as_markup()

def get_order_actions_keyboard(order_number: str) -> InlineKeyboardMarkup:
    """Клавиатура с действиями для конкретного заказа"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="🔄 Изменить статус", callback_data=f"change_status_{order_number}")
    )
    builder.row(
        InlineKeyboardButton(text="📋 К списку заказов", callback_data="show_orders"),
        InlineKeyboardButton(text="🔙 В меню", callback_data="back_to_menu")
    )
    
    return builder.as_markup()

def get_status_change_keyboard(order_number: str, statuses: list) -> InlineKeyboardMarkup:
    """Клавиатура для изменения статуса заказа"""
    builder = InlineKeyboardBuilder()
    
    for status in statuses:
        status_id = status.get("id")
        status_name = status.get("name")
        builder.row(
            InlineKeyboardButton(
                text=f"{status_name}",
                callback_data=f"set_status_{order_number}_{status_id}"
            )
        )
    
    builder.row(
        InlineKeyboardButton(text="🔙 Назад к заказу", callback_data=f"order_{order_number}")
    )
    
    return builder.as_markup()
