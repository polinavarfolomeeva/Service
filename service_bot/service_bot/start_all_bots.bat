@echo off
chcp 65001 >nul
echo Запуск всех ботов автосервиса...

start cmd /k "python main.py"
echo Основной бот запущен в отдельном окне

start cmd /k "python staff_bot.py"
echo Бот сотрудников запущен в отдельном окне

start cmd /k "python service_bot.py"
echo Бот механиков СТО запущен в отдельном окне

echo.
echo Все боты запущены. Закройте это окно, чтобы остановить все боты.
echo Для остановки отдельного бота закройте соответствующее окно командной строки.
echo.

pause
