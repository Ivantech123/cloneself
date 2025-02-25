# AI Persona Bot

Телеграм-бот, который имитирует стиль общения на основе сообщений из Telegram и постов из Дзен.

## Быстрый старт

### Автоматическая установка (рекомендуется)

1. Скачайте этот репозиторий
   ```
   git clone <your-repo-url>
   cd tg_channel_parser
   ```

2. Запустите `install_all.bat`
   - Автоматически установит Python, если его нет
   - Создаст виртуальное окружение
   - Установит все зависимости
   - Создаст необходимые файлы конфигурации

3. Настройте файл `.env` (как получить все ключи - см. [подробное руководство](SETUP_GUIDE.md))
   ```
   OPENAI_API_KEY=your_openai_api_key_here    # https://platform.openai.com/api-keys
   TELEGRAM_BOT_TOKEN=your_bot_token_here     # @BotFather в Telegram
   API_ID=your_telegram_api_id_here           # my.telegram.org
   API_HASH=your_telegram_api_hash_here       # my.telegram.org
   PHONE=your_phone_number_here               # Ваш номер телефона
   ```

4. Запустите `start.bat` для запуска бота

👉 **[Подробное руководство по установке и настройке](SETUP_GUIDE.md)**

### Ручная установка

Если автоматическая установка не сработала:

1. Установите [Python 3.8 или выше](https://www.python.org/downloads/)
   - При установке обязательно отметьте "Add Python to PATH"

2. Запустите `setup.bat`

3. Следуйте инструкциям выше начиная с пункта 3

## Возможности

- Анализ стиля сообщений из Telegram и постов из Дзен
- Умное определение тона сообщений (юмор/серьезность)
- Контекстные ответы с учетом истории диалога
- Поддержка эмодзи и форматирования
- 🎤 Голосовые сообщения с помощью OpenAI TTS
  - Команда /voice для включения/выключения
  - Реалистичный голос
  - Поддержка русского языка

## Структура проекта

- `ai_persona_bot.py` - основной файл бота
- `install_all.bat` - скрипт полной установки (включая Python)
- `setup.bat` - скрипт установки зависимостей
- `start.bat` - скрипт запуска
- `.env` - файл с конфигурацией
- `requirements.txt` - зависимости проекта
- `SETUP_GUIDE.md` - подробное руководство по установке

## Требования

- Windows 7/8/10/11
- Интернет-подключение для установки
- OpenAI API ключ ([получить здесь](https://platform.openai.com/api-keys))
- Telegram Bot Token ([@BotFather](https://t.me/BotFather))
- Telegram API credentials ([my.telegram.org](https://my.telegram.org/auth))

## Поддержка

Если у вас возникли проблемы:
1. Прочитайте [подробное руководство](SETUP_GUIDE.md)
2. Проверьте раздел "Возможные проблемы и решения" в руководстве
3. Создайте issue в репозитории с описанием проблемы
