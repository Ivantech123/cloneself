@echo off
echo Starting setup...

:: Проверяем наличие Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Python not found! Please install Python 3.8 or higher from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

:: Создаем виртуальное окружение
echo Creating virtual environment...
python -m venv venv

:: Активируем виртуальное окружение
echo Activating virtual environment...
call venv\Scripts\activate.bat

:: Устанавливаем зависимости
echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

:: Создаем файл .env если его нет
if not exist .env (
    echo Creating .env file...
    echo OPENAI_API_KEY=your_openai_api_key_here> .env
    echo TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here>> .env
    echo API_ID=your_telegram_api_id_here>> .env
    echo API_HASH=your_telegram_api_hash_here>> .env
    echo PHONE=your_phone_number_here>> .env
)

echo.
echo Setup completed!
echo.
echo Next steps:
echo 1. Edit .env file and add your API keys and tokens
echo 2. Run 'start.bat' to start the bot
echo.
pause
