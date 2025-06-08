import re
from datetime import datetime
from aiogram.types import Message
from loguru import logger

def format_message(message, message_type="info"):

    emoji_dict = {
        "success": "✅",
        "info": "ℹ️",
        "warning": "⚠️",
        "error": "❌"
    }
    emoji = emoji_dict.get(message_type, "ℹ️")

    return f"{emoji} {message}"

def get_main_menu_text(user_name):

    return (
        f"<b>🌟 Добро пожаловать, {user_name}! 🌟</b>\n\n"
        f"Я бот автосервиса \"АвтоМастер\". С моей помощью вы можете:\n\n"
        f"• 🚗 <b>Найти</b> необходимые запчасти для вашего автомобиля\n"
        f"• 🔧 <b>Узнавать</b> о доступных услугах и их стоимости\n"
        f"• 📱 <b>Записываться</b> на обслуживание в удобное время\n"
        f"• 👤 <b>Управлять</b> своим профилем и отслеживать заказы\n\n"
        f"<i>Мы заботимся о вашем автомобиле так же, как и вы! ✅</i>\n\n"
        f"Пожалуйста, выберите раздел, который вас интересует:"
    )

def format_price(price):
    try:
        price_str = f"{float(price):,.2f}".replace(",", " ")

        if price_str.endswith(".00"):
            price_str = price_str[:-3]
        return f"{price_str} ₽"
    except (ValueError, TypeError):
        return "Цена недоступна"

def format_orders_list(orders: list) -> str:
    """Форматирование списка заказов для отображения"""
    if not orders:
        return "Список заказов пуст"
    
    result = ""
    for i, order in enumerate(orders, 1):
        order_number = order.get("number", "б/н")
        date_str = order.get("date", "")
        status = order.get("status", "Нет статуса")
        amount = order.get("amount", 0)
        client_name = order.get("client", {}).get("name", "Неизвестно")
        client_phone = order.get("client", {}).get("phone", "Нет телефона")
        
        if date_str:
            try:
                date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                date_str = date.strftime("%d.%m.%Y %H:%M")
            except Exception:
                pass
        
        result += (
            f"{i}. <b>Заказ №{order_number}</b>\n"
            f"📅 Дата: {date_str}\n"
            f"👤 Клиент: {client_name}\n"
            f"📱 Телефон: {client_phone}\n"
            f"💰 Сумма: {amount} руб.\n"
            f"📊 Статус: {status}\n\n"
        )
    
    return result

def format_order_details(order: dict) -> str:
    """Форматирование деталей заказа"""
    order_number = order.get("number", "б/н")
    date_str = order.get("date", "")
    status = order.get("status", "Нет статуса")
    amount = order.get("amount", 0)
    comment = order.get("comment", "")
    client_name = order.get("client", {}).get("name", "Неизвестно")
    client_phone = order.get("client", {}).get("phone", "Нет телефона")
    
    if date_str:
        try:
            date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            date_str = date.strftime("%d.%m.%Y %H:%M")
        except Exception:
            pass
    
    result = (
        f"<b>Заказ №{order_number}</b>\n\n"
        f"📅 <b>Дата:</b> {date_str}\n"
        f"👤 <b>Клиент:</b> {client_name}\n"
        f"📱 <b>Телефон:</b> {client_phone}\n"
        f"💰 <b>Сумма:</b> {amount} руб.\n"
        f"📊 <b>Статус:</b> {status}\n"
    )
    
    if comment:
        result += f"💬 <b>Комментарий:</b> {comment}\n"
    
    items = order.get("items", [])
    if items:
        result += "\n<b>Позиции заказа:</b>\n"
        for i, item in enumerate(items, 1):
            item_name = item.get("name", "Неизвестная позиция")
            quantity = item.get("quantity", 1)
            price = item.get("price", 0)
            item_amount = item.get("amount", 0)
            
            result += (
                f"{i}. {item_name}\n"
                f"   Кол-во: {quantity} × {price} = {item_amount} руб.\n"
            )
    
    return result

def format_service_orders_list(orders: list) -> str:
    """Форматирование списка заказов СТО для отображения"""
    if not orders:
        return "Список заказов СТО пуст"
    
    result = ""
    for i, order in enumerate(orders, 1):
        order_number = order.get("number", "б/н")
        date_str = order.get("date", "")
        status = order.get("status", "Нет статуса")
        amount = order.get("amount", 0)
        client_name = order.get("client", {}).get("name", "Неизвестно")
        car = order.get("car", "Не указан")
        
        if date_str:
            try:
                date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                date_str = date.strftime("%d.%m.%Y %H:%M")
            except Exception:
                pass
        
        result += (
            f"{i}. <b>Заказ СТО №{order_number}</b>\n"
            f"📅 Дата: {date_str}\n"
            f"👤 Клиент: {client_name}\n"
            f"🚗 Автомобиль: {car}\n"
            f"💰 Сумма: {amount} руб.\n"
            f"📊 Статус: {status}\n\n"
        )
    
    return result

def format_service_order_details(order: dict) -> str:
    """Форматирование деталей заказа СТО"""
    order_number = order.get("number", "б/н")
    date_str = order.get("date", "")
    status = order.get("status", "Нет статуса")
    amount = order.get("amount", 0)
    comment = order.get("comment", "")
    client_name = order.get("client", {}).get("name", "Неизвестно")    
    client_phone = order.get("client", {}).get("phone", "Нет телефона")
    car = order.get("car", "Не указан")
    start_date_str = order.get("start_date", "")
    end_date_str = order.get("end_date", "")
    
    mechanic_raw = order.get("mechanic", "")
    if not mechanic_raw or mechanic_raw == "<>":
        mechanic = "Не назначен"
    else:
        mechanic = mechanic_raw.replace("<", "&lt;").replace(">", "&gt;")
    
    date_format = "%d.%m.%Y %H:%M"
    if date_str:
        try:
            date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            date_str = date.strftime(date_format)
        except Exception:
            pass
    
    if start_date_str:
        try:
            start_date = datetime.fromisoformat(start_date_str.replace("Z", "+00:00"))
            start_date_str = start_date.strftime(date_format)
        except Exception:
            pass
    
    if end_date_str:
        try:
            end_date = datetime.fromisoformat(end_date_str.replace("Z", "+00:00"))
            end_date_str = end_date.strftime(date_format)
        except Exception:
            pass
    
    result = (
        f"<b>Заказ СТО №{order_number}</b>\n\n"
        f"📅 <b>Дата создания:</b> {date_str}\n"
        f"👤 <b>Клиент:</b> {client_name}\n"
        f"📱 <b>Телефон:</b> {client_phone}\n"
        f"🚗 <b>Автомобиль:</b> {car}\n"
        f"🕒 <b>Запланировано с:</b> {start_date_str}\n"
        f"🕒 <b>Запланировано до:</b> {end_date_str}\n"
        f"👨‍🔧 <b>Механик:</b> {mechanic}\n"
        f"💰 <b>Сумма:</b> {amount} руб.\n"
        f"📊 <b>Статус:</b> {status}\n"
    )
    
    if comment:
        result += f"💬 <b>Комментарий:</b> {comment}\n"
    
    items = order.get("items", [])
    if items:
        result += "\n<b>Запчасти и услуги:</b>\n"
        for i, item in enumerate(items, 1):
            item_name = item.get("name", "Неизвестная позиция")
            quantity = item.get("quantity", 1)
            price = item.get("price", 0)
            item_amount = item.get("amount", 0)
            
            result += (
                f"{i}. {item_name}\n"
                f"   Кол-во: {quantity} × {price} = {item_amount} руб.\n"
            )
    return result

def validate_phone(phone):

    pattern = r'^\+7\d{10}$'
    return bool(re.match(pattern, phone))

def validate_email(email):

    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def format_date(date_str, input_format="%Y-%m-%dT%H:%M:%S", output_format="%d.%m.%Y %H:%M"):

    try:
        date_obj = datetime.strptime(date_str, input_format)
        return date_obj.strftime(output_format)
    except (ValueError, TypeError):
        return "Дата недоступна"

def format_product_info(product):

    if not product:
        return "Информация о товаре недоступна"

    if isinstance(product, dict) and "product" in product:
        product = product["product"]

    name = product.get("name", product.get("Наименование", "Без названия"))

    price_value = product.get("price", product.get("Цена", 0))
    price = format_price(price_value)

    description = product.get("description", product.get("Описание", "Описание отсутствует"))

    stock = product.get("stock", product.get("КоличествоНаСкладе", 0))
    category = product.get("category_name", product.get("КатегорияНаименование", ""))
    supplier = product.get("supplier", product.get("ПоставщикНаименование", ""))
    in_stock = "В наличии" if product.get("in_stock", product.get("ВНаличии", False)) else "Нет в наличии"

    text = f"<b>{name}</b>\n\n"
    text += f"<b>Цена:</b> {price}\n"
    text += f"<b>Статус:</b> {in_stock}\n"
    text += f"<b>Наличие:</b> {stock} шт.\n"

    if category:
        text += f"<b>Категория:</b> {category}\n"

    if supplier:
        text += f"<b>Поставщик:</b> {supplier}\n"

    text += f"\n<b>Описание:</b>\n{description}\n"

    return text

def format_service_info(service):

    if not service:
        return "Информация об услуге недоступна"

    name = service.get("name", service.get("Наименование", "Без названия"))
    price = format_price(service.get("price", service.get("Цена", 0)))
    description = service.get("description", service.get("Описание", "Описание отсутствует"))

    duration = service.get("execution_time", service.get("duration", "Нет данных о длительности"))

    duration_text = "Нет данных о длительности"
    if duration and duration != "Нет данных о длительности":
        duration_text = f"{duration}"

    text = f"<b>{name}</b>\n\n"
    text += f"<b>Цена:</b> {price}\n"
    text += f"<b>Длительность:</b> {duration_text} мин.\n\n"
    text += f"<b>Описание:</b>\n{description}\n"

    return text

def format_support_info():
    return """
📞 <b>Техническая поддержка</b>

Для связи с оператором:
<b>Телефон:</b> +7 (495) 123-45-67  
<b>Telegram:</b> @autoservice_support  

🕒 Работаем ежедневно с 9:00 до 21:00
"""