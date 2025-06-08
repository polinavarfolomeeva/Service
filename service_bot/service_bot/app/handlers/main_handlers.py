from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from loguru import logger
from app.utils.formatting import format_support_info
from app.keyboards.keyboards import get_back_button
from aiogram.utils.markdown import bold, code

from app.keyboards.keyboards import get_main_menu
from app.utils.formatting import get_main_menu_text

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):

    user_name = message.from_user.first_name
    greeting_text = get_main_menu_text(user_name)

    await message.answer(greeting_text, reply_markup=get_main_menu(), parse_mode="HTML")

@router.message(Command("help"))
async def cmd_help(message: Message):
    help_text = """
<b>Помощь</b>

Для работы с ботом используйте кнопки в меню:
- <b>Категории:</b> Просмотр каталога товаров.
- <b>Все товары:</b> Показать весь ассортимент.
- <b>Услуги:</b> Записаться на диагностику или ремонт.
- <b>Личный кабинет:</b> Управление заказами и профилем.
- <b>О сервисе:</b> Информация о компании.

Если возникли вопросы, позвоните по номеру +79210271678.
"""
    await message.answer(help_text, parse_mode="HTML")

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


@router.callback_query(F.data == "my_cars")
async def order_history_handler(callback: CallbackQuery):
    logger.info("Обработчик 'my_cars' вызван!")

    cars_text = (
        f"<b>✅ Выполненные услуги</b>\n\n"
        
        f"Работы по автомобилю: Kia Seed (Номер заказа: 000000001\n\n"
        f"- Дата начала: 23.04.2025\n"
        f"- Заказчик: Иванов И.И.\n"
        f"- Сотрудник: Оператор Стас\n"
        f"- Статус: Выполнен\n\n"
        
        f"Товары:\n\n"
        f"| N | Работа/деталь                | Количество | Цена   | Сумма   |\n"
        f"|---|------------------------------|------------|--------|---------|\n"
        f"| 1 | Тормозные колодки Brembo     | 1          | 2 500  | 2 500   |\n"
        f"| 2 | Амортизатор задний Toyota    | 1          | 3 500  | 3 500   |\n\n"
        
        f"Общая стоимость: 6 000 ₽|\n"
    )
    try:
        if callback.message.text:
            await callback.message.edit_text(
                text=cars_text,
                reply_markup=get_back_to_profile_keyboard(),
                parse_mode="HTML"
            )
        else:
            await callback.message.answer(
                text=cars_text,
                reply_markup=get_back_to_profile_keyboard(),
                parse_mode="HTML"
            )
    except Exception as e:
        logger.error(f"Ошибка при отправке истории заказов: {e}")
        await callback.message.answer("Произошла ошибка при отображении истории заказов.")

    await callback.answer()


@router.message(F.text == "Личный кабинет")
async def show_profile(message: Message):
    await message.answer("<b>👤 Личный кабинет</b>\n\nВыберите действие:", reply_markup=get_profile_keyboard(), parse_mode="HTML")

def get_back_to_profile_keyboard():
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main"),
        width=1
    )
    return builder.as_markup()

@router.callback_query(F.data == "promotions")
async def promotions_handler(callback: CallbackQuery):
    logger.info("Обработчик 'promotions' вызван!")

    promotions_text = (
        f"<b>🎁 Акции и скидки</b>\n\n"
        
        f"<b>🔥 Специальное предложение:</b>\n"
        f"<i>Замена масла — по цене двух литров вместо трёх!</i>\n"
        f"- Только до конца месяца\n"
        f"- При заказе услуги замены масла — <code>бесплатная диагностика двигателя</code>\n\n"
        
        f"<b>🚗 Для владельцев Toyota:</b>\n"
        f"- Скидка <code>15%</code> на оригинальные запчасти\n"
        f"- Требуется предъявить ПТС или СТС при оплате\n\n"
        
        f"<b>💥 Бонус за отзыв:</b>\n"
        f"- Оставьте отзыв о сервисе и получите <code>скидку 10%</code> на следующую услугу\n"
        f"- Отзыв можно оставить на нашем сайте или в Telegram-боте"
    )

    try:
        if callback.message.text:
            await callback.message.edit_text(
                text=promotions_text,
                reply_markup=get_back_to_profile_keyboard(),
                parse_mode="HTML"
            )
        else:
            await callback.message.answer(
                text=promotions_text,
                reply_markup=get_back_to_profile_keyboard(),
                parse_mode="HTML"
            )
    except Exception as e:
        logger.error(f"Ошибка при отправке акций: {e}")
        await callback.message.answer("Произошла ошибка при отображении акций.")

    await callback.answer()

@router.callback_query(F.data.in_(["add_to_cart_", "book_service_"]))
async def process_not_implemented(callback: CallbackQuery):

    feature_names = {
        "my_car": "Информация об автомобиле",
        "my_orders": "Мои заказы",
        "about": "О сервисе",
    }

    if callback.data.startswith("add_to_cart_"):
        await callback.answer("🔧 Функция добавления в корзину находится в разработке. Мы сообщим, когда она станет доступна!", show_alert=True)
        return

    if callback.data.startswith("book_service_"):
        await callback.answer("📅 Онлайн-запись на услугу скоро будет доступна! Пока вы можете позвонить нам для записи.", show_alert=True)
        return

    feature_name = feature_names.get(callback.data, "Эта функция")

    await callback.message.edit_text(
        f"<b>🔧 {feature_name} - в разработке</b>\n\n"
        f"Уважаемый клиент!\n\n"
        f"Мы постоянно работаем над улучшением сервиса. "
        f"В настоящий момент данная функция находится в активной разработке "
        f"и скоро станет доступна.\n\n"
        f"<i>Спасибо за понимание и терпение! Мы ценим ваше доверие.</i>",
        reply_markup=get_main_menu(),
        parse_mode="HTML"
    )

    await callback.answer()

@router.callback_query(F.data == "about")
async def about_handler(callback: CallbackQuery):
    logger.info("Обработчик 'about' вызван!")

    about_text = (
        f"<b>ℹ️ О сервисе</b>\n\n"
        
        f"Название компании: ООО «АвтоСервис Плюс»\n"
        f"Адрес: Санкт-Петербург, ул. Любытинская, д. 8\n"
        f"Телефон: +7 (921) 027-16-78\n"
        f"Email: info@autoserviceplus.ru\n\n"
        
        f"Режим работы:\n"
        f"Пн–Сб: 9:00 – 20:00\n"
        f"Воскресенье: выходной\n\n"
        
        f"Услуги:\n"
        f"• Диагностика и ремонт автомобилей\n"
        f"• Замена масла, фильтров и других расходников\n"
        f"• Ремонт ходовой, тормозной системы\n"
        f"• Заправка и ремонт кондиционеров\n"
        f"• Установка доп. оборудования\n"
        f"• Продажа запчастей и автоаксессуаров\n\n"
        
        f"Мы работаем с 2015 года, обслуживая как частных клиентов, так и корпоративных заказчиков.\n"
        f"Наша цель — сделать ваш автомобиль надёжным и безопасным!"
    )

    try:
        if callback.message.text:
            await callback.message.edit_text(
                text=about_text,
                reply_markup=get_back_to_profile_keyboard(),
                parse_mode="HTML"
            )
        else:
            await callback.message.answer(
                text=about_text,
                reply_markup=get_back_to_profile_keyboard(),
                parse_mode="HTML"
            )
    except Exception as e:
        logger.error(f"Ошибка при отправке информации о сервисе: {e}")
        await callback.message.answer("Произошла ошибка при отображении информации о сервисе.")

    await callback.answer()

@router.callback_query(
    ~F.data.startswith("product_") &
    ~F.data.startswith("service_") &
    ~F.data.startswith("category_") &
    ~F.data.in_(["catalog_products", "catalog_services", "catalog_categories", 
                 "back_to_products", "back_to_services", "back_to_categories",
                 "login", "register", "logout", "profile", "cancel"])
)
async def process_other_callbacks(callback: CallbackQuery):

    logger.warning(f"Неизвестный callback_data: {callback.data}")
    await callback.answer("🔧 Эта функция находится в разработке", show_alert=True)


@router.message()
async def process_other_messages(message: Message):

    user_name = message.from_user.first_name

    await message.answer(
        f"<b>👋 Здравствуйте, {user_name}!</b>\n\n"
        f"К сожалению, я не понимаю текстовые сообщения. "
        f"Пожалуйста, используйте меню бота для навигации.\n\n"
        f"<i>Если у вас возникли вопросы, вы всегда можете начать заново, используя команду /start</i>",
        reply_markup=get_main_menu(),
        parse_mode="HTML"
    )



