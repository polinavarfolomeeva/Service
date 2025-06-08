from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from loguru import logger

from app.keyboards.keyboards import get_main_menu, get_auth_menu, get_cancel_keyboard, get_profile_keyboard
from app.keyboards.register_keyboards import get_contact_keyboard, get_login_choice_keyboard
from app.services.api_service import api_service
from app.utils.formatting import format_message, get_main_menu_text
from app.utils.auth import validate_phone, validate_email, format_phone_for_api

router = Router()

user_auth_cache = {}

class AuthStates(StatesGroup):

    waiting_for_login = State()
    waiting_for_password = State()
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_email = State()
    waiting_for_login_choice = State()
    waiting_for_manual_login = State()
    waiting_for_register_password = State()  

    def __init__(self):
        super().__init__()
        self.messages_to_delete = []

@router.callback_query(F.data == "profile")
async def process_profile(callback: CallbackQuery):

    user_id = callback.from_user.id
    user_name = callback.from_user.first_name
    
    is_authenticated = user_auth_cache.get(user_id, False)

    if is_authenticated:
        text = (
            f"<b>👤 Личный кабинет</b>\n\n"
            f"Добро пожаловать в личный кабинет, {user_name}!\n\n"
            f"Здесь вы можете:\n"
            f"• Управлять своим профилем\n"
            f"• Просматривать историю заказов\n"
            f"• Отслеживать статус текущих заказов\n"
            f"• Получать персональные предложения"
        )
        await callback.message.edit_text(
            text,
            reply_markup=get_profile_keyboard(),
            parse_mode="HTML"
        )
    else:
        text = (
            f"<b>👤 Личный кабинет</b>\n\n"
            f"В личном кабинете вы можете:\n"
            f"• Управлять своим профилем\n"
            f"• Просматривать историю заказов\n"
            f"• Отслеживать статус текущих заказов\n"
            f"• Получать персональные предложения\n\n"
            f"<i>Для полного доступа к функциям личного кабинета необходимо войти или зарегистрироваться.</i>"
        )
        await callback.message.edit_text(
            text,
            reply_markup=get_auth_menu(),
            parse_mode="HTML"
        )

    await callback.answer()

@router.callback_query(F.data == "login")
async def process_login(callback: CallbackQuery, state: FSMContext):

    await state.update_data(auth_messages_to_delete=[])

    await state.set_state(AuthStates.waiting_for_login)

    sent_message = await callback.message.edit_text(
        "<b>🔑 Авторизация</b>\n\n"
        "Пожалуйста, введите ваш логин (email):",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )

    user_data = await state.get_data()
    auth_messages_to_delete = user_data.get("auth_messages_to_delete", [])
    auth_messages_to_delete.append(sent_message.message_id)
    await state.update_data(auth_messages_to_delete=auth_messages_to_delete)

    await callback.answer()

@router.message(AuthStates.waiting_for_login)
async def process_login_input(message: Message, state: FSMContext):

    await state.update_data(login=message.text)

    user_data = await state.get_data()
    auth_messages_to_delete = user_data.get("auth_messages_to_delete", [])
    auth_messages_to_delete.append(message.message_id)

    await state.set_state(AuthStates.waiting_for_password)

    sent_message = await message.answer(
        "🔒 Введите пароль:",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )

    auth_messages_to_delete.append(sent_message.message_id)
    await state.update_data(auth_messages_to_delete=auth_messages_to_delete)

@router.message(AuthStates.waiting_for_password)
async def process_password_input(message: Message, state: FSMContext):

    await state.update_data(password=message.text)

    user_data = await state.get_data()
    auth_messages_to_delete = user_data.get("auth_messages_to_delete", [])
    auth_messages_to_delete.append(message.message_id)
    await state.update_data(auth_messages_to_delete=auth_messages_to_delete)

    data = await state.get_data()
    login = data.get("login")
    password = data.get("password")

    response = await api_service.login_user({"login": login, "password": password})

    auth_messages_to_delete = data.get("auth_messages_to_delete", [])

    if response.get("status") == 200 and response.get("data", {}).get("user", {}):
        user_id = message.from_user.id
        user_auth_cache[user_id] = True
        
        for msg_id in auth_messages_to_delete:
            try:
                await message.bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
            except Exception as e:
                logger.error(f"Не удалось удалить сообщение {msg_id}: {e}")

        try:
            await message.delete()
        except Exception as e:
            logger.error(f"Не удалось удалить сообщение с паролем: {e}")

        user_data = response.get("data", {}).get("user", {})
        user_name = user_data.get("name", "Пользователь")

        greeting_text = get_main_menu_text(user_name)

        await message.answer(
            greeting_text,
            reply_markup=get_main_menu(),
            parse_mode="HTML"
        )
    else:
        if isinstance(response.get("data"), dict) and response.get("data", {}).get("message"):
            error_message = response.get("data", {}).get("message")
        elif response.get("status") != 200:
            error_message = f"Ошибка сервера (код {response.get('status')})"
        else:
            error_message = "Неверный логин или пароль"

        await message.answer(
            format_message(f"Ошибка входа: {error_message}", "error"),
            reply_markup=get_auth_menu(),
            parse_mode="HTML"
        )

    await state.clear()

@router.callback_query(F.data == "logout")
async def process_logout(callback: CallbackQuery):
    user_id = callback.from_user.id
    
    response = await api_service.logout_user()

    if response.get("status") == 200:
        user_auth_cache.pop(user_id, None)
        
        await callback.message.edit_text(
            format_message("Вы успешно вышли из системы.", "success"),
            reply_markup=get_auth_menu(),
            parse_mode="HTML"
        )
    else:
        await callback.message.edit_text(
            format_message("Произошла ошибка при выходе из системы.", "error"),
            reply_markup=get_profile_keyboard(),
            parse_mode="HTML"
        )

    await callback.answer()

@router.callback_query(F.data == "cancel")
async def process_cancel(callback: CallbackQuery, state: FSMContext):

    current_state = await state.get_state()

    if current_state:
        await state.clear()

    await callback.message.edit_text(
        "<b>✅ Операция отменена</b>\n\n"
        "Действие было успешно отменено. Вы можете продолжить использование бота.\n\n"
        "<i>Чем ещё мы можем вам помочь?</i>",
        reply_markup=get_main_menu(),
        parse_mode="HTML"
    )

    await callback.answer("Операция успешно отменена")

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

#
@router.callback_query(F.data == "register")
async def process_register(callback: CallbackQuery, state: FSMContext):

    await state.update_data(messages_to_delete=[])

    await state.set_state(AuthStates.waiting_for_name)

    sent_message = await callback.message.edit_text(
        "<b>📝 Регистрация</b>\n\n"
        "Пожалуйста, введите ваше ФИО:",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )

    user_data = await state.get_data()
    messages_to_delete = user_data.get("messages_to_delete", [])
    messages_to_delete.append(sent_message.message_id)
    await state.update_data(messages_to_delete=messages_to_delete)

    await callback.answer()

@router.message(AuthStates.waiting_for_name)
async def process_name_input(message: Message, state: FSMContext):

    await state.update_data(name=message.text)

    user_data = await state.get_data()
    messages_to_delete = user_data.get("messages_to_delete", [])
    messages_to_delete.append(message.message_id)

    await state.set_state(AuthStates.waiting_for_phone)

    sent_message = await message.answer(
        "📱 Пожалуйста, поделитесь своим контактом, нажав на кнопку ниже:",
        reply_markup=get_contact_keyboard(),
        parse_mode="HTML"
    )

    messages_to_delete.append(sent_message.message_id)
    await state.update_data(messages_to_delete=messages_to_delete)

@router.message(AuthStates.waiting_for_phone, F.contact)
async def process_contact_input(message: Message, state: FSMContext):

    phone = message.contact.phone_number

    user_data = await state.get_data()
    messages_to_delete = user_data.get("messages_to_delete", [])
    messages_to_delete.append(message.message_id)
    await state.update_data(messages_to_delete=messages_to_delete)

    if not validate_phone(phone):
        sent_message = await message.answer(
            format_message("Получен некорректный номер телефона. Пожалуйста, попробуйте еще раз.", "warning"),
            reply_markup=get_contact_keyboard(),
            parse_mode="HTML"
        )

        messages_to_delete.append(sent_message.message_id)
        await state.update_data(messages_to_delete=messages_to_delete)
        return

    formatted_phone = format_phone_for_api(phone)

    await state.update_data(phone=phone, formatted_phone=formatted_phone)

    await state.set_state(AuthStates.waiting_for_email)

    sent_message = await message.answer(
        "📧 Введите ваш email:",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="HTML"
    )

    messages_to_delete = user_data.get("messages_to_delete", [])
    messages_to_delete.append(sent_message.message_id)
    await state.update_data(messages_to_delete=messages_to_delete)

@router.message(AuthStates.waiting_for_phone)
async def process_manual_phone_input(message: Message, state: FSMContext):

    phone = message.text

    user_data = await state.get_data()
    messages_to_delete = user_data.get("messages_to_delete", [])
    messages_to_delete.append(message.message_id)
    await state.update_data(messages_to_delete=messages_to_delete)

    if not validate_phone(phone):
        sent_message = await message.answer(
            format_message("Пожалуйста, введите корректный номер телефона или поделитесь контактом.", "warning"),
            reply_markup=get_contact_keyboard(),
            parse_mode="HTML"
        )

        messages_to_delete.append(sent_message.message_id)
        await state.update_data(messages_to_delete=messages_to_delete)
        return

    formatted_phone = format_phone_for_api(phone)

    await state.update_data(phone=phone, formatted_phone=formatted_phone)

    await state.set_state(AuthStates.waiting_for_email)

    sent_message = await message.answer(
        "📧 Введите ваш email:",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="HTML"
    )

    messages_to_delete.append(sent_message.message_id)
    await state.update_data(messages_to_delete=messages_to_delete)

@router.message(AuthStates.waiting_for_email)
async def process_email_input(message: Message, state: FSMContext):

    email = message.text

    user_data = await state.get_data()
    messages_to_delete = user_data.get("messages_to_delete", [])
    messages_to_delete.append(message.message_id)
    await state.update_data(messages_to_delete=messages_to_delete)

    if not validate_email(email):
        sent_message = await message.answer(
            format_message("Пожалуйста, введите корректный email адрес.", "warning"),
            reply_markup=get_cancel_keyboard(),
            parse_mode="HTML"
        )
        messages_to_delete.append(sent_message.message_id)
        await state.update_data(messages_to_delete=messages_to_delete)
        return

    await state.update_data(email=email)

    await state.set_state(AuthStates.waiting_for_login_choice)

    sent_message = await message.answer(
        "🔑 Хотите использовать введенный email в качестве логина?",
        reply_markup=get_login_choice_keyboard(),
        parse_mode="HTML"
    )

    messages_to_delete.append(sent_message.message_id)
    await state.update_data(messages_to_delete=messages_to_delete)

@router.callback_query(F.data == "use_email_as_login", AuthStates.waiting_for_login_choice)
async def process_use_email_as_login(callback: CallbackQuery, state: FSMContext):

    user_data = await state.get_data()
    email = user_data.get("email", "")

    messages_to_delete = user_data.get("messages_to_delete", [])
    if callback.message and callback.message.message_id:
        messages_to_delete.append(callback.message.message_id)

    await state.update_data(login=email, messages_to_delete=messages_to_delete)

    await state.set_state(AuthStates.waiting_for_register_password)

    sent_message = await callback.message.edit_text(
        f"✅ Email <b>{email}</b> будет использоваться как логин.\n\n"
        "🔒 Придумайте пароль (не менее 6 символов):",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )

    if sent_message and sent_message.message_id:
        messages_to_delete.append(sent_message.message_id)
        await state.update_data(messages_to_delete=messages_to_delete)

    await callback.answer()

@router.callback_query(F.data == "manual_login", AuthStates.waiting_for_login_choice)
async def process_manual_login(callback: CallbackQuery, state: FSMContext):

    user_data = await state.get_data()
    messages_to_delete = user_data.get("messages_to_delete", [])
    if callback.message and callback.message.message_id:
        messages_to_delete.append(callback.message.message_id)

    await state.set_state(AuthStates.waiting_for_manual_login)

    sent_message = await callback.message.edit_text(
        "👤 Введите логин, который хотите использовать:",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )

    if sent_message and sent_message.message_id:
        messages_to_delete.append(sent_message.message_id)
        await state.update_data(messages_to_delete=messages_to_delete)

    await callback.answer()

@router.message(AuthStates.waiting_for_manual_login)
async def process_manual_login_input(message: Message, state: FSMContext):

    user_data = await state.get_data()
    messages_to_delete = user_data.get("messages_to_delete", [])
    messages_to_delete.append(message.message_id)
    await state.update_data(messages_to_delete=messages_to_delete)

    if len(message.text) < 3:
        sent_message = await message.answer(
            format_message("Логин должен содержать не менее 3 символов. Пожалуйста, попробуйте еще раз.", "warning"),
            reply_markup=get_cancel_keyboard(),
            parse_mode="HTML"
        )

        messages_to_delete.append(sent_message.message_id)
        await state.update_data(messages_to_delete=messages_to_delete)
        return

    await state.update_data(login=message.text)

    await state.set_state(AuthStates.waiting_for_register_password)

    sent_message = await message.answer(
        "🔒 Придумайте пароль (не менее 6 символов):",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )

    messages_to_delete.append(sent_message.message_id)
    await state.update_data(messages_to_delete=messages_to_delete)

@router.message(AuthStates.waiting_for_register_password)
async def process_password_for_register(message: Message, state: FSMContext):

    user_data = await state.get_data()
    messages_to_delete = user_data.get("messages_to_delete", [])
    messages_to_delete.append(message.message_id)
    await state.update_data(messages_to_delete=messages_to_delete)

    if len(message.text) < 6:
        sent_message = await message.answer(
            format_message("Пароль должен содержать не менее 6 символов. Пожалуйста, попробуйте еще раз.", "warning"),
            reply_markup=get_cancel_keyboard(),
            parse_mode="HTML"
        )

        messages_to_delete.append(sent_message.message_id)
        await state.update_data(messages_to_delete=messages_to_delete)
        return

    await state.update_data(password=message.text)

    user_data = await state.get_data()

    name = user_data.get("name", "")
    phone = user_data.get("phone", "")
    email = user_data.get("email", "")
    login = user_data.get("login", "")

    register_data = {
        "name": name,
        "phone": user_data.get("formatted_phone", format_phone_for_api(phone)),
        "email": email,
        "login": login,
        "password": user_data.get("password", "")
    }

    if not validate_phone(phone):
        await message.answer(
            format_message("Введен некорректный номер телефона. Пожалуйста, начните регистрацию заново.", "error"),
            reply_markup=get_main_menu(),
            parse_mode="HTML"
        )
        await state.clear()
        return

    logger.debug(f"Отправка запроса на регистрацию: {register_data}")
    logger.debug(f"Используем эндпоинт: /auth/register")
    response = await api_service.register_user(register_data)

    messages_to_delete = user_data.get("messages_to_delete", [])

    if response.get("status") in [200, 201]:

        for msg_id in messages_to_delete:
            try:
                await message.bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
            except Exception as e:
                logger.error(f"Не удалось удалить сообщение {msg_id}: {e}")

        try:
            await message.delete()
        except Exception as e:
            logger.error(f"Не удалось удалить сообщение с паролем: {e}")

        await state.clear()

        user_data_from_api = response.get("data", {}).get("user", {})

        await message.answer(
            f"<b>✅ Регистрация успешно завершена!</b>\n\n"
            f"<b>Ваши данные:</b>\n"
            f"👤 ФИО: <b>{user_data_from_api.get('name', name)}</b>\n"
            f"📱 Телефон: <b>+7{user_data_from_api.get('phone', phone)}</b>\n"
            f"📧 Email: <b>{user_data_from_api.get('email', email)}</b>\n"
            f"🔑 Логин: <b>{user_data_from_api.get('username', login)}</b>\n\n"
            f"<i>Теперь вы можете войти в систему, используя свои учетные данные.</i>",
            reply_markup=get_auth_menu(),
            parse_mode="HTML"
        )
    else:

        if isinstance(response.get("data"), dict):
            error_message = response.get("data", {}).get("message", "Не удалось зарегистрироваться")
        else:
            error_message = f"Ошибка (код {response.get('status')}): {response.get('data', 'Неизвестная ошибка')}"

        await message.answer(
            format_message(f"Ошибка регистрации: {error_message}", "error"),
            reply_markup=get_auth_menu(),
            parse_mode="HTML"
        )

        await state.clear()

@router.callback_query(F.data == "logout")
async def process_logout(callback: CallbackQuery):

    response = await api_service.logout_user()

    if response.get("status") == 200:

        await callback.message.edit_text(
            format_message("Вы успешно вышли из системы.", "success"),
            reply_markup=get_auth_menu(),
            parse_mode="HTML"
        )
    else:

        await callback.message.edit_text(
            format_message("Произошла ошибка при выходе из системы.", "error"),
            reply_markup=get_profile_keyboard(),
            parse_mode="HTML"
        )

    await callback.answer()

@router.callback_query(F.data == "cancel")
async def process_cancel(callback: CallbackQuery, state: FSMContext):

    current_state = await state.get_state()

    if current_state:
        await state.clear()

    await callback.message.edit_text(
        "<b>✅ Операция отменена</b>\n\n"
        "Действие было успешно отменено. Вы можете продолжить использование бота.\n\n"
        "<i>Чем ещё мы можем вам помочь?</i>",
        reply_markup=get_main_menu(),
        parse_mode="HTML"
    )

    await callback.answer("Операция успешно отменена")

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