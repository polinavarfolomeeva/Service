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

ITEMS_PER_PAGE = 10  

@router.callback_query(F.data == "catalog_products")
async def process_catalog_products(callback: CallbackQuery, state: FSMContext):

    await callback.message.edit_text(
        "<b>🔄 Загружаем каталог товаров...</b>\n"
        "Пожалуйста, подождите...",
        reply_markup=None,
        parse_mode="HTML"
    )

    response = await api_service.get_products()
    logger.debug(f"Получен ответ от API (products): {response}")

    if response.get("status") == 200 and "data" in response:

        products_data = response.get("data", [])

        logger.debug(f"Данные продуктов: {products_data}")

        if isinstance(products_data, dict) and 'products' in products_data:
            products = products_data.get('products', [])
        else:
            products = products_data

        formatted_products = []

        if isinstance(products, list):
            for product in products:
                if isinstance(product, dict):

                    if 'Наименование' in product:
                        product_id = product.get("Идентификатор", "")
                        if isinstance(product_id, dict) and "id" in product_id:
                            product_id = product_id.get("id", "")
                            
                        category = product.get("Категория", "")
                        if isinstance(category, dict) and "id" in category:
                            category = category.get("id", "")
                            
                        formatted_products.append({
                            "id": product_id,
                            "code": product.get("Код", ""), 
                            "name": product.get("Наименование", "Товар"),
                            "price": product.get("Цена", "По запросу"),
                            "description": product.get("Описание", ""),
                            "stock": product.get("КоличествоНаСкладе", 0),
                            "category": category,
                            "category_name": product.get("КатегорияНаименование", "")
                        })
                    else:

                        if "code" not in product and "id" in product:
                            product["code"] = product["id"]  
                        formatted_products.append(product)
                elif isinstance(product, str):

                    formatted_products.append({
                        "id": product, 
                        "name": product, 
                        "price": "По запросу",
                        "code": product  
                    })
                else:

                    logger.warning(f"Неизвестный тип данных продукта: {type(product)}, значение: {product}")

        if formatted_products:

            await state.update_data(
                products=formatted_products,
                current_page=1,
                total_pages=math.ceil(len(formatted_products) / ITEMS_PER_PAGE)
            )

            await show_products_page(callback, state, 1)
        else:
            await callback.message.edit_text(
                "<b>😔 Каталог товаров пуст</b>\n\n"
                "К сожалению, в данный момент в каталоге нет доступных товаров.\n"
                "Пожалуйста, загляните позже или свяжитесь с нами для получения дополнительной информации.",
                reply_markup=get_main_menu(),
                parse_mode="HTML"
            )
    else:
        error_message = response.get("data", {}).get("message", "Не удалось загрузить каталог товаров")
        await callback.message.edit_text(
            f"<b>❌ Ошибка</b>\n\n{error_message}\n\n"
            "Пожалуйста, попробуйте позже или обратитесь в службу поддержки.",
            reply_markup=get_main_menu(),
            parse_mode="HTML"
        )

    await callback.answer()

async def show_products_page(callback: CallbackQuery, state: FSMContext, page: int):

    state_data = await state.get_data()
    products = state_data.get("products", [])
    total_pages = state_data.get("total_pages", 1)

    if page < 1:
        page = 1
    elif page > total_pages:
        page = total_pages

    await state.update_data(current_page=page)

    start_idx = (page - 1) * ITEMS_PER_PAGE
    end_idx = min(start_idx + ITEMS_PER_PAGE, len(products))

    current_page_items = products[start_idx:end_idx]

    text = (
        "<b>🛒 Каталог автозапчастей и аксессуаров</b>\n\n"
        "Мы предлагаем широкий выбор качественных товаров для вашего автомобиля.\n\n"
        "<i>Выберите товар из списка ниже:</i>"
    )

    if total_pages > 1:
        text += f"\n\nСтраница {page} из {total_pages}"

    await callback.message.edit_text(
        text,
        reply_markup=get_products_keyboard(current_page_items, page, total_pages),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("products_page_"))
async def process_products_pagination(callback: CallbackQuery, state: FSMContext):

    page = int(callback.data.split("_")[-1])

    await show_products_page(callback, state, page)
    await callback.answer()

@router.callback_query(F.data == "catalog_services")
async def process_catalog_services(callback: CallbackQuery, state: FSMContext):

    await callback.message.edit_text(
        "<b>🔄 Загружаем каталог услуг...</b>\n"
        "Пожалуйста, подождите...",
        reply_markup=None,
        parse_mode="HTML"
    )

    response = await api_service.get_services()
    logger.debug(f"Получен ответ от API (services): {response}")

    if response.get("status") == 200 and "data" in response:

        services_data = response.get("data", [])

        logger.debug(f"Данные услуг: {services_data}")

        if isinstance(services_data, dict) and 'services' in services_data:
            services = services_data.get('services', [])
        else:
            services = services_data

        formatted_services = []

        if isinstance(services, list):
            for service in services:
                if isinstance(service, dict):

                    if 'Наименование' in service:                        
                        service_id = service.get("Идентификатор", "")
                        if isinstance(service_id, dict) and "id" in service_id:
                            service_id = service_id.get("id", "")
                            
                        formatted_services.append({
                            "id": service_id,
                            "code": service.get("Код", ""), 
                            "name": service.get("Наименование", "Услуга"),
                            "price": service.get("Цена", "По запросу"),
                            "description": service.get("Описание", ""),
                            "duration": service.get("Длительность", 0)
                        })
                    else:

                        if "code" not in service and "id" in service:
                            service["code"] = service["id"]  
                        formatted_services.append(service)
                elif isinstance(service, str):

                    formatted_services.append({
                        "id": service, 
                        "name": service, 
                        "price": "По запросу",
                        "code": service  
                    })
                else:

                    logger.warning(f"Неизвестный тип данных услуги: {type(service)}, значение: {service}")

        if formatted_services:

            await state.update_data(
                services=formatted_services,
                current_services_page=1,
                total_services_pages=math.ceil(len(formatted_services) / ITEMS_PER_PAGE)
            )

            await show_services_page(callback, state, 1)
        else:
            await callback.message.edit_text(
                "<b>😔 Каталог услуг пуст</b>\n\n"
                "К сожалению, в данный момент в каталоге нет доступных услуг.\n"
                "Пожалуйста, загляните позже или свяжитесь с нами для получения дополнительной информации.",
                reply_markup=get_main_menu(),
                parse_mode="HTML"
            )
    else:
        error_message = response.get("data", {}).get("message", "Не удалось загрузить каталог услуг")
        await callback.message.edit_text(
            f"<b>❌ Ошибка</b>\n\n{error_message}\n\n"
            "Пожалуйста, попробуйте позже или обратитесь в службу поддержки.",
            reply_markup=get_main_menu(),
            parse_mode="HTML"
        )

    await callback.answer()

async def show_services_page(callback: CallbackQuery, state: FSMContext, page: int):

    state_data = await state.get_data()
    services = state_data.get("services", [])
    total_pages = state_data.get("total_services_pages", 1)

    if page < 1:
        page = 1
    elif page > total_pages:
        page = total_pages

    await state.update_data(current_services_page=page)

    start_idx = (page - 1) * ITEMS_PER_PAGE
    end_idx = min(start_idx + ITEMS_PER_PAGE, len(services))

    current_page_items = services[start_idx:end_idx]

    text = (
        "<b>🔧 Услуги автосервиса</b>\n\n"
        "Мы предлагаем полный спектр услуг по обслуживанию и ремонту автомобилей.\n"
        "Наши мастера имеют многолетний опыт и используют современное оборудование.\n\n"
        "<i>Выберите услугу из списка ниже:</i>"
    )

    if total_pages > 1:
        text += f"\n\nСтраница {page} из {total_pages}"

    await callback.message.edit_text(
        text,
        reply_markup=get_services_keyboard(current_page_items, page, total_pages),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("services_page_"))
async def process_services_pagination(callback: CallbackQuery, state: FSMContext):

    page = int(callback.data.split("_")[-1])

    await show_services_page(callback, state, page)
    await callback.answer()

@router.callback_query(F.data.startswith("product_"))
async def process_product_detail(callback: CallbackQuery, state: FSMContext):
    product_id = callback.data.split("_")[1]

    state_data = await state.get_data()
    all_products = state_data.get("products", []) + state_data.get("category_products", [])

    selected_product = next((p for p in all_products if p.get("id") == product_id), None)

    product_code = ""
    if selected_product:
        product_code = selected_product.get("code", selected_product.get("Код", ""))
        
        if not product_code:
            product_code = selected_product.get("id", selected_product.get("Идентификатор", ""))
            if isinstance(product_code, dict) and "id" in product_code:
                product_code = product_code.get("id", "")

    if not product_code:
        await callback.message.edit_text(
            "❌ Ошибка: Не удалось найти код товара. Пожалуйста, выберите товар из списка снова.",
            reply_markup=get_main_menu(),
            parse_mode="HTML"
        )
        await callback.answer()
        return

    await callback.message.edit_text(
        "🔄 Загружаю информацию о товаре...",
        reply_markup=None
    )

    response = await api_service.get_product_by_id(product_code)
    logger.debug(f"Ответ API для товара {product_code}: статус {response.get('status')}")

    if response.get("status") == 200 and "data" in response:
        product = response.get("data", {})

        if isinstance(product, dict) and "product" in product:
            product = product["product"]

        logger.debug(f"Полученные данные о товаре после обработки: {product}")

        if product:

            product_info = format_product_info(product)

            await callback.message.edit_text(
                product_info,
                reply_markup=get_product_detail_keyboard(product_id),
                parse_mode="HTML"
            )
        else:
            await callback.message.edit_text(
                "😔 К сожалению, информация о товаре недоступна.",
                reply_markup=get_products_keyboard(),
                parse_mode="HTML"
            )
    else:
        error_message = response.get("data", {}).get("message", "Не удалось загрузить информацию о товаре")
        logger.error(f"Ошибка при получении информации о товаре {product_code}: {error_message}")
        await callback.message.edit_text(
            format_message(error_message, "error"),
            reply_markup=get_products_keyboard(),
            parse_mode="HTML"
        )

    await callback.answer()

@router.callback_query(F.data == "back_to_products")
async def process_back_to_products(callback: CallbackQuery, state: FSMContext):

    await process_catalog_products(callback, state)
    await callback.answer()

@router.callback_query(F.data.startswith("service_"))
async def process_service_detail(callback: CallbackQuery, state: FSMContext):
    service_id = callback.data.split("_")[1]

    state_data = await state.get_data()
    all_services = state_data.get("services", [])
    selected_service = next((s for s in all_services if s.get("id") == service_id), None)

    service_code = ""
    if selected_service:
        service_code = selected_service.get("code", selected_service.get("Код", ""))
        
        if not service_code:
            service_code = selected_service.get("id", selected_service.get("Идентификатор", ""))
            if isinstance(service_code, dict) and "id" in service_code:
                service_code = service_code.get("id", "")

    if not service_code:
        await callback.message.edit_text(
            "❌ Ошибка: Не удалось найти код услуги. Пожалуйста, выберите услугу из списка снова.",
            reply_markup=get_main_menu(),
            parse_mode="HTML"
        )
        await callback.answer()
        return

    await callback.message.edit_text(
        "🔄 Загружаю информацию об услуге...",
        reply_markup=None
    )

    response = await api_service.get_service_by_id(service_code)

    if response.get("status") == 200 and "data" in response:

        data = response.get("data", {})
        service = data.get("service", data)  

        if service:

            logger.debug(f"Данные услуги для форматирования: {service}")

            service_info = format_service_info(service)

            await callback.message.edit_text(
                service_info,
                reply_markup=get_service_detail_keyboard(service_id),
                parse_mode="HTML"
            )
        else:
            await callback.message.edit_text(
                "😔 К сожалению, информация об услуге недоступна.",
                reply_markup=get_services_keyboard(),
                parse_mode="HTML"
            )
    else:
        error_message = response.get("data", {}).get("message", "Не удалось загрузить информацию об услуге")
        await callback.message.edit_text(
            format_message(error_message, "error"),
            reply_markup=get_services_keyboard(),
            parse_mode="HTML"
        )

    await callback.answer()

@router.callback_query(F.data == "back_to_services")
async def process_back_to_services(callback: CallbackQuery, state: FSMContext):

    await process_catalog_services(callback, state)
    await callback.answer()

@router.callback_query(F.data == "catalog_categories")
async def process_catalog_categories(callback: CallbackQuery, state: FSMContext):

    await callback.message.edit_text(
        "<b>🔄 Загружаем категории товаров...</b>\n"
        "Пожалуйста, подождите...",
        reply_markup=None,
        parse_mode="HTML"
    )

    response = await api_service.get_categories()
    logger.debug(f"Получен ответ от API (categories): {response}")

    if response.get("status") == 200 and "data" in response:

        categories_data = response.get("data", [])

        logger.debug(f"Данные категорий: {categories_data}")

        formatted_categories = []
        
        if isinstance(categories_data, dict) and 'categories' in categories_data:
            categories_list = categories_data.get('categories', [])

            for category in categories_list:
                if isinstance(category, dict):
                    category_id = category.get("Идентификатор", category.get("Код", ""))
                    
                    if isinstance(category_id, dict) and "id" in category_id:
                        category_id = category_id.get("id", "")
                        
                    formatted_categories.append({
                        "id": category_id,
                        "name": category.get("Наименование", "Категория"),
                        "description": category.get("Описание", ""),
                        "code": category.get("Код", "")
                    })
                elif isinstance(category, str):
                    formatted_categories.append({"id": category, "name": category})        
        elif isinstance(categories_data, list):
            for category in categories_data:
                if isinstance(category, dict):
                    if "Наименование" in category:
                        category_id = category.get("Идентификатор", category.get("Код", ""))
                        
                        if isinstance(category_id, dict) and "id" in category_id:
                            category_id = category_id.get("id", "")
                            
                        formatted_categories.append({
                            "id": category_id,
                            "name": category.get("Наименование", "Категория"),
                            "description": category.get("Описание", ""),
                            "code": category.get("Код", "")
                        })
                    else:
                        formatted_categories.append(category)
                elif isinstance(category, str):

                    formatted_categories.append({"id": category, "name": category})
                else:

                    logger.warning(f"Неизвестный тип данных категории: {type(category)}, значение: {category}")

        logger.debug(f"Форматированные категории: {formatted_categories}")

        if formatted_categories:

            await state.update_data(
                categories=formatted_categories,
                current_categories_page=1,
                total_categories_pages=math.ceil(len(formatted_categories) / ITEMS_PER_PAGE)
            )

            await show_categories_page(callback, state, 1)
        else:
            await callback.message.edit_text(
                "<b>😔 Каталог категорий пуст</b>\n\n"
                "К сожалению, в данный момент в каталоге нет доступных категорий.\n"
                "Пожалуйста, загляните позже или свяжитесь с нами для получения дополнительной информации.",
                reply_markup=get_main_menu(),
                parse_mode="HTML"
            )
    else:
        error_message = response.get("data", {}).get("message", "Не удалось загрузить каталог категорий")
        await callback.message.edit_text(
            f"<b>❌ Ошибка</b>\n\n{error_message}\n\n"
            "Пожалуйста, попробуйте позже или обратитесь в службу поддержки.",
            reply_markup=get_main_menu(),
            parse_mode="HTML"
        )

    await callback.answer()

async def show_categories_page(callback: CallbackQuery, state: FSMContext, page: int):

    state_data = await state.get_data()
    categories = state_data.get("categories", [])
    total_pages = state_data.get("total_categories_pages", 1)

    if page < 1:
        page = 1
    elif page > total_pages:
        page = total_pages

    await state.update_data(current_categories_page=page)

    start_idx = (page - 1) * ITEMS_PER_PAGE
    end_idx = min(start_idx + ITEMS_PER_PAGE, len(categories))

    current_page_items = categories[start_idx:end_idx]

    text = (
        "<b>📂 Категории товаров</b>\n\n"
        "Выберите интересующую вас категорию товаров из списка ниже:"
    )

    if total_pages > 1:
        text += f"\n\nСтраница {page} из {total_pages}"

    await callback.message.edit_text(
        text,
        reply_markup=get_categories_keyboard(current_page_items, page, total_pages),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("categories_page_"))
async def process_categories_pagination(callback: CallbackQuery, state: FSMContext):

    page = int(callback.data.split("_")[-1])

    await show_categories_page(callback, state, page)
    await callback.answer()

@router.callback_query(F.data.startswith("category_"))
async def process_category_products(callback: CallbackQuery, state: FSMContext):

    category_id = callback.data.split("_")[1]
    logger.debug(f"Выбрана категория с ID: {category_id}")

    state_data = await state.get_data()
    all_categories = state_data.get("categories", [])
    logger.debug(f"Все категории: {all_categories}")
    
    selected_category = next((cat for cat in all_categories if cat.get("id") == category_id), {"name": "Категория"})
    logger.debug(f"Выбранная категория: {selected_category}")
    
    category_name = selected_category.get("name", "Категория")

    await callback.message.edit_text(
        f"<b>🔄 Загружаем товары категории \"{category_name}\"...</b>\n"
        "Пожалуйста, подождите...",
        reply_markup=None,
        parse_mode="HTML"
    )
    await state.update_data(selected_category=selected_category)
    
    category_code = ""
    
    if selected_category:
        category_code = selected_category.get("code", "")
        if not category_code:
            category_code = selected_category.get("Код", "")
        
        if not category_code:
            category_code = category_id
    
    logger.debug(f"Финальный код категории для API запроса: {category_code}")

    if not category_code:
        await callback.message.edit_text(
            f"<b>❌ Ошибка</b>\n\nНе удалось найти код категории \"{category_name}\".\n"
            f"Пожалуйста, выберите другую категорию или обратитесь к администратору.",
            reply_markup=get_main_menu(),
            parse_mode="HTML"
        )
        await callback.answer()
        return

    response = await api_service.get_category_by_id(category_code)
    logger.debug(f"Получен ответ от API (category by ID): {response}")

    products_data = []

    if response.get("status") == 200 and "data" in response and isinstance(response["data"], dict):
        category_data = response["data"]

        if "products" in category_data and isinstance(category_data["products"], list):
            products_data = category_data["products"]

    if not products_data:
        response = await api_service.get_products_by_category(category_code)
        logger.debug(f"Получен ответ от API (products by category): {response}")

        if response.get("status") == 200 and "data" in response:

            products_data = response.get("data", [])

    logger.debug(f"Данные товаров по категории: {products_data}")

    if isinstance(products_data, dict) and 'products' in products_data:
        products = products_data.get('products', [])
    else:
        products = products_data

    formatted_products = []    
    if isinstance(products, list):
        for product in products:
            if isinstance(product, dict):
                if 'Наименование' in product:
                    product_id = product.get("Идентификатор", "")
                    if isinstance(product_id, dict) and "id" in product_id:
                        product_id = product_id.get("id", "")
                        
                    category = product.get("Категория", "")
                    if isinstance(category, dict) and "id" in category:
                        category = category.get("id", "")

                    formatted_products.append({
                        "id": product_id,
                        "code": product.get("Код", ""),
                        "name": product.get("Наименование", "Товар"),
                        "price": product.get("Цена", "По запросу"),
                        "description": product.get("Описание", ""),
                        "stock": product.get("КоличествоНаСкладе", 0),
                        "category": category,
                        "category_name": product.get("КатегорияНаименование", "")
                    })
                else:
                    formatted_products.append(product)
            elif isinstance(product, str):
                formatted_products.append({"id": product, "name": product, "price": "По запросу"})

    if formatted_products:

        await state.update_data(
            category_products=formatted_products,
            current_category_page=1,
            total_category_pages=math.ceil(len(formatted_products) / ITEMS_PER_PAGE)
        )

        await show_category_products_page(callback, state, 1)
    else:
        await callback.message.edit_text(
            f"<b>😔 В категории \"{category_name}\" нет товаров</b>\n\n"
            f"К сожалению, в данный момент в этой категории нет доступных товаров.\n"
            f"Пожалуйста, выберите другую категорию или загляните позже.",
            reply_markup=get_categories_keyboard(all_categories, 1, math.ceil(len(all_categories) / ITEMS_PER_PAGE)),
            parse_mode="HTML"
        )

    await callback.answer()

async def show_category_products_page(callback: CallbackQuery, state: FSMContext, page: int):

    state_data = await state.get_data()
    products = state_data.get("category_products", [])
    total_pages = state_data.get("total_category_pages", 1)
    selected_category = state_data.get("selected_category", {"name": "Категория"})
    category_name = selected_category.get("name", "Категория")

    if page < 1:
        page = 1
    elif page > total_pages:
        page = total_pages

    await state.update_data(current_category_page=page)

    start_idx = (page - 1) * ITEMS_PER_PAGE
    end_idx = min(start_idx + ITEMS_PER_PAGE, len(products))

    current_page_items = products[start_idx:end_idx]

    text = (
        f"<b>🛒 Товары категории \"{category_name}\"</b>\n\n"
        f"Выберите интересующий вас товар из списка ниже:"
    )

    if total_pages > 1:
        text += f"\n\nСтраница {page} из {total_pages}"

    builder = InlineKeyboardBuilder()

    for product in current_page_items:
        name = product.get('name', 'Товар')
        price = product.get('price', 'По запросу')
        product_id = product.get('id', '')

        price_text = f"{price}₽" if isinstance(price, (int, float)) else price

        builder.row(
            InlineKeyboardButton(
                text=f"{name} - {price_text}",
                callback_data=f"product_{product_id}"
            )
        )

    if total_pages > 1:
        pagination_buttons = []

        if page > 1:
            pagination_buttons.append(
                InlineKeyboardButton(
                    text="◀️",
                    callback_data=f"category_products_page_{page - 1}"
                )
            )

        pagination_buttons.append(
            InlineKeyboardButton(
                text=f"{page} из {total_pages}",
                callback_data="category_products_current_page"
            )
        )

        if page < total_pages:
            pagination_buttons.append(
                InlineKeyboardButton(
                    text="▶️",
                    callback_data=f"category_products_page_{page + 1}"
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

    await callback.message.edit_text(
        text,
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("category_products_page_"))
async def process_category_products_pagination(callback: CallbackQuery, state: FSMContext):

    page = int(callback.data.split("_")[-1])

    await show_category_products_page(callback, state, page)
    await callback.answer()

@router.callback_query(F.data == "back_to_categories")
async def process_back_to_categories(callback: CallbackQuery, state: FSMContext):

    state_data = await state.get_data()
    categories = state_data.get("categories", [])
    current_page = state_data.get("current_categories_page", 1)
    total_pages = state_data.get("total_categories_pages", 1)

    if current_page < 1:
        current_page = 1
    elif current_page > total_pages:
        current_page = total_pages

    start_idx = (current_page - 1) * ITEMS_PER_PAGE
    end_idx = min(start_idx + ITEMS_PER_PAGE, len(categories))

    current_page_items = categories[start_idx:end_idx]

    text = (
        "<b>📂 Категории товаров</b>\n\n"
        "Выберите интересующую вас категорию товаров из списка ниже:"
    )

    if total_pages > 1:
        text += f"\n\nСтраница {current_page} из {total_pages}"

    await callback.message.edit_text(
        text,
        reply_markup=get_categories_keyboard(current_page_items, current_page, total_pages),
        parse_mode="HTML"
    )

    await callback.answer()
