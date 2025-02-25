from telethon.sync import TelegramClient
from telethon.tl.types import MessageService
from datetime import datetime
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Учетные данные Telegram API
API_ID = int(os.getenv('API_ID', '0'))  # Преобразуем в число
API_HASH = os.getenv('API_HASH', '')
PHONE = os.getenv('PHONE', '')

# Имя канала для парсинга (без @)
CHANNEL = 'a2wars'

def save_results(messages):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'parsed_messages_{timestamp}.txt'
    
    with open(filename, 'w', encoding='utf-8') as f:
        for msg in messages:
            f.write(f"ID сообщения: {msg['id']}\n")
            f.write(f"Дата: {msg['date']}\n")
            f.write(f"Просмотры: {msg['views']}\n")
            f.write(f"Есть медиа: {msg['has_media']}\n")
            f.write(f"Текст: {msg['text']}\n")
            f.write("-" * 50 + "\n")

def main():
    # Проверяем наличие учетных данных
    if API_ID == 0 or not API_HASH or not PHONE:
        print("Ошибка: Проверьте файл .env - не все учетные данные указаны корректно")
        return

    print(f"Подключаемся к Telegram...")
    
    try:
        # Создаем клиент и подключаемся
        with TelegramClient('session_name', API_ID, API_HASH) as client:
            # Ensure you're authorized
            if not client.is_user_authorized():
                client.send_code_request(PHONE)
                client.sign_in(PHONE, input('Введите код подтверждения: '))

            print(f"Начинаем парсинг канала: {CHANNEL}")
            
            # Получаем информацию о канале
            channel = client.get_entity(CHANNEL)
            
            # Собираем сообщения
            messages = []
            for message in client.iter_messages(channel):
                # Пропускаем служебные сообщения и репосты
                if isinstance(message, MessageService) or message.forward:
                    continue
                
                # Создаем словарь с данными сообщения
                msg_data = {
                    'id': message.id,
                    'date': message.date.strftime('%Y-%m-%d %H:%M:%S'),
                    'text': message.text,
                    'views': message.views,
                    'has_media': bool(message.media)
                }
                messages.append(msg_data)
                
                # Выводим прогресс
                print(f"Обработано сообщение ID: {message.id}")
            
            # Сохраняем результаты
            save_results(messages)
            print(f"Парсинг завершен. Всего сообщений: {len(messages)}")
            
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")

if __name__ == '__main__':
    main()
