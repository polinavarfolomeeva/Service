from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

def get_main_menu() -> InlineKeyboardMarkup:

    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="📂 Категории", callback_data="catalog_categories"),
        InlineKeyboardButton(text="🛒 Все товары", callback_data="catalog_products"),
        width=1
    )

    builder.row(
        InlineKeyboardButton(text="🔧 Услуги", callback_data="catalog_services"),
        InlineKeyboardButton(text="👤 Личный кабинет", callback_data="profile"),
        width=1
    )

    builder.row(
        InlineKeyboardButton(text="ℹ️ О сервисе", callback_data="about"),
        width=1
    )

    return builder.as_markup()

def get_auth_menu() -> InlineKeyboardMarkup:

    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="🔑 Войти", callback_data="login"),
        InlineKeyboardButton(text="📝 Зарегистрироваться", callback_data="register"),
        width=1
    )

    builder.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main"),
        width=1
    )

    return builder.as_markup()

def get_catalog_menu(categories=None) -> InlineKeyboardMarkup:

    builder = InlineKeyboardBuilder()

    if categories:
        for cat in categories:
            builder.row(
                InlineKeyboardButton(
                    text=cat.get("name", "Категория"),
                    callback_data=f"category_{cat.get('id')}"
                )
            )

    builder.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main"),
        width=1
    )

    return builder.as_markup()

def get_products_keyboard(products=None, current_page=1, total_pages=1) -> InlineKeyboardMarkup:

    builder = InlineKeyboardBuilder()

    if products:
        for product in products:

            if not isinstance(product, dict):

                continue

            name = product.get('name', 'Товар')
            if not name and 'Наименование' in product:
                name = product.get('Наименование', 'Товар')

            price = product.get('price', 'По запросу')
            if not price and 'Цена' in product:
                price = product.get('Цена', 'По запросу')

            product_id = product.get('id', '')
            if not product_id and 'Идентификатор' in product:
                product_id = product.get('Идентификатор', '')

            if not product_id:
                continue

            price_text = f"{price}₽" if isinstance(price, (int, float)) else price

            builder.row(
                InlineKeyboardButton(
                    text=f"{name} - {price_text}",
                    callback_data=f"product_{product_id}"
                )
            )

    if total_pages > 1:
        pagination_buttons = []

        if current_page > 1:
            pagination_buttons.append(
                InlineKeyboardButton(
                    text="◀️",
                    callback_data=f"products_page_{current_page - 1}"
                )
            )

        pagination_buttons.append(
            InlineKeyboardButton(
                text=f"{current_page} из {total_pages}",
                callback_data="products_current_page"
            )
        )

        if current_page < total_pages:
            pagination_buttons.append(
                InlineKeyboardButton(
                    text="▶️",
                    callback_data=f"products_page_{current_page + 1}"
                )
            )

        builder.row(*pagination_buttons)

    builder.row(
        InlineKeyboardButton(text="🔙 Назад к категориям", callback_data="back_to_categories"),
        width=1
    )

    builder.row(
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main"),
        width=1
    )

    return builder.as_markup()

def get_services_keyboard(services=None, current_page=1, total_pages=1) -> InlineKeyboardMarkup:

    builder = InlineKeyboardBuilder()

    if services:
        for service in services:

            if not isinstance(service, dict):

                continue

            name = service.get('name', 'Услуга')
            if not name and 'Наименование' in service:
                name = service.get('Наименование', 'Услуга')

            price = service.get('price', 'По запросу')
            if not price and 'Цена' in service:
                price = service.get('Цена', 'По запросу')

            service_id = service.get('id', '')
            if not service_id and 'Идентификатор' in service:
                service_id = service.get('Идентификатор', '')

            if not service_id:
                continue

            price_text = f"{price}₽" if isinstance(price, (int, float)) else price

            builder.row(
                InlineKeyboardButton(
                    text=f"{name} - {price_text}",
                    callback_data=f"service_{service_id}"
                )
            )

    if total_pages > 1:
        pagination_buttons = []

        if current_page > 1:
            pagination_buttons.append(
                InlineKeyboardButton(
                    text="◀️",
                    callback_data=f"services_page_{current_page - 1}"
                )
            )

        pagination_buttons.append(
            InlineKeyboardButton(
                text=f"{current_page} из {total_pages}",
                callback_data="services_current_page"
            )
        )

        if current_page < total_pages:
            pagination_buttons.append(
                InlineKeyboardButton(
                    text="▶️",
                    callback_data=f"services_page_{current_page + 1}"
                )
            )

        builder.row(*pagination_buttons)

    builder.row(
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main"),
        width=1
    )

    return builder.as_markup()

def get_categories_keyboard(categories=None, current_page=1, total_pages=1) -> InlineKeyboardMarkup:

    builder = InlineKeyboardBuilder()

    if categories:
        for category in categories:

            if not isinstance(category, dict):

                continue

            name = category.get('name', 'Категория')
            if not name and 'Наименование' in category:
                name = category.get('Наименование', 'Категория')

            category_id = category.get('id', '')
            if not category_id and 'Идентификатор' in category:
                category_id = category.get('Идентификатор', '')

            if not category_id:
                continue

            builder.row(
                InlineKeyboardButton(
                    text=f"📁 {name}",
                    callback_data=f"category_{category_id}"
                )
            )

    if total_pages > 1:
        pagination_buttons = []

        if current_page > 1:
            pagination_buttons.append(
                InlineKeyboardButton(
                    text="◀️",
                    callback_data=f"categories_page_{current_page - 1}"
                )
            )

        pagination_buttons.append(
            InlineKeyboardButton(
                text=f"{current_page} из {total_pages}",
                callback_data="categories_current_page"
            )
        )

        if current_page < total_pages:
            pagination_buttons.append(
                InlineKeyboardButton(
                    text="▶️",
                    callback_data=f"categories_page_{current_page + 1}"
                )
            )

        builder.row(*pagination_buttons)

    builder.row(
        InlineKeyboardButton(text="🛒 Все товары", callback_data="catalog_products"),
        width=1
    )

    builder.row(
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main"),
        width=1
    )

    return builder.as_markup()

def get_product_detail_keyboard(product_id) -> InlineKeyboardMarkup:

    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="🛒 Добавить в корзину", callback_data=f"add_to_cart_{product_id}"),
        width=1
    )

    builder.row(
        InlineKeyboardButton(text="🔙 Назад к товарам", callback_data="back_to_products"),
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main"),
        width=1
    )

    return builder.as_markup()

def get_service_detail_keyboard(service_id) -> InlineKeyboardMarkup:

    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="📅 Записаться", callback_data=f"book_service_{service_id}"),
        width=1
    )

    builder.row(
        InlineKeyboardButton(text="🔙 Назад к услугам", callback_data="back_to_services"),
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main"),
        width=1
    )

    return builder.as_markup()

def get_auth_menu() -> InlineKeyboardMarkup:
    """
    Возвращает клавиатуру для неавторизованного пользователя в личном кабинете
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔑 Войти", callback_data="login"),
            InlineKeyboardButton(text="📝 Зарегистрироваться", callback_data="register")
        ],
        [
            InlineKeyboardButton(text="« Назад", callback_data="back_to_main")
        ]
    ])
    return keyboard

def get_profile_keyboard() -> InlineKeyboardMarkup:
    """
    Возвращает клавиатуру для авторизованного пользователя в личном кабинете
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📦 История заказов", callback_data="order_history"),
            InlineKeyboardButton(text="🎁 Акции", callback_data="promotions")
        ],
        [
            InlineKeyboardButton(text="🚗 Выполненные услуги", callback_data="my_cars"),
            #InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings")
            InlineKeyboardButton(text="🚪 Выйти", callback_data="logout")
        ],
        [
            #InlineKeyboardButton(text="🚪 Выйти", callback_data="logout")
        ],
        [
            InlineKeyboardButton(text="« Назад", callback_data="back_to_main")
        ]
    ])
    return keyboard

def get_cancel_keyboard() -> InlineKeyboardMarkup:

    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="❌ Отменить", callback_data="cancel"),
        InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_auth"),
        width=1
    )

    return builder.as_markup()

def get_back_button():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Назад")]],
        resize_keyboard=True
    )