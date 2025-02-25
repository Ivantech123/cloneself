@echo off
:: Активируем виртуальное окружение
call venv\Scripts\activate.bat

:: Проверяем наличие .env файла
if not exist .env (
    echo Error: .env file not found!
    echo Please run setup.bat first and configure your .env file
    pause
    exit /b 1
)

:: Запускаем бота
echo Starting AI Persona Bot...
python ai_persona_bot.py
pause
