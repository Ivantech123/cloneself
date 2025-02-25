import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI
import json
from datetime import datetime
import logging
import re

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

class PersonaBot:
    def __init__(self, openai_api_key, telegram_token):
        self.client = OpenAI(api_key=openai_api_key)
        self.telegram_token = telegram_token
        self.messages = []
        self.system_prompt = ""
        self.conversation_history = {}
        self.tone_patterns = {
            'humor': [
                r'#ЮС',
                r'😂|😅|🤣',
                r'шутк[аи]',
                r'юмор',
                r'сатира'
            ],
            'serious': [
                r'#важно',
                r'#срочно',
                r'внимание',
                r'серьезно',
                r'#warning'
            ]
        }
        
    def analyze_message_tone(self, text):
        """Анализирует тон сообщения"""
        text = text.lower()
        tone_scores = {
            'humor': 0,
            'serious': 0
        }
        
        for tone, patterns in self.tone_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                tone_scores[tone] += len(matches)
                
        return tone_scores
        
    def load_telegram_messages(self, filename):
        """Загружает сообщения и анализирует их тон"""
        print("Загрузка сообщений...")
        message_tones = []
        
        # Загружаем сообщения из Telegram
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
            message_blocks = content.split('-' * 50)
            
            for block in message_blocks:
                if not block.strip():
                    continue
                    
                lines = block.strip().split('\n')
                message_data = {}
                
                for line in lines:
                    if line.startswith('Текст:'):
                        text = line.split(':', 1)[1].strip()
                        message_data['text'] = text
                        tone_scores = self.analyze_message_tone(text)
                        message_data['tone'] = 'humor' if tone_scores['humor'] > tone_scores['serious'] else 'serious'
                        
                if 'text' in message_data:
                    self.messages.append(message_data)
                    message_tones.append(message_data['tone'])
        
        # Загружаем сообщения из Дзен
        zen_file = "zen_posts.txt"
        if os.path.exists(zen_file):
            print("Загрузка постов из Дзен...")
            with open(zen_file, 'r', encoding='utf-8') as f:
                zen_content = f.read()
                zen_blocks = zen_content.split('\n---\n')
                
                for block in zen_blocks:
                    if not block.strip():
                        continue
                    
                    text = block.strip()
                    message_data = {
                        'text': text,
                        'source': 'zen'
                    }
                    tone_scores = self.analyze_message_tone(text)
                    message_data['tone'] = 'humor' if tone_scores['humor'] > tone_scores['serious'] else 'serious'
                    self.messages.append(message_data)
                    message_tones.append(message_data['tone'])
        
        # Анализируем распределение тона в сообщениях
        humor_count = message_tones.count('humor')
        serious_count = message_tones.count('serious')
        total_messages = len(message_tones)
        
        humor_ratio = humor_count / total_messages if total_messages > 0 else 0
        
        # Создаем системный промпт с учетом анализа тона
        sample_humor = [msg['text'] for msg in self.messages[:5] if msg.get('tone') == 'humor']
        sample_serious = [msg['text'] for msg in self.messages[:5] if msg.get('tone') == 'serious']
        
        # Добавляем больше контекста из Дзен для серьезных тем
        zen_serious = [msg['text'] for msg in self.messages if msg.get('source') == 'zen' and msg.get('tone') == 'serious'][:3]
        if zen_serious:
            sample_serious.extend(zen_serious)
        
        self.system_prompt = f"""Ты - бот, который точно имитирует стиль общения реального человека, основываясь на его сообщениях из Telegram и постах в Дзен. 
Анализ показывает, что {humor_ratio*100:.1f}% сообщений содержат юмор или сатиру.

Примеры юмористических сообщений:
{chr(10).join(f'- {msg}' for msg in sample_humor)}

Примеры серьезных сообщений и постов:
{chr(10).join(f'- {msg}' for msg in sample_serious)}

Правила общения:
1. Если в сообщении пользователя есть намек на юмор или тема легкая - отвечай с юмором, используя похожий стиль шуток.
2. Если тема серьезная (особенно про мошенничество, безопасность, финансы) - отвечай серьезно и по делу, используя стиль из Дзен-постов.
3. Используй хештеги #ЮС для юмора и #важно для серьезных тем, как в примерах.
4. Сохраняй характерные обороты речи и манеру общения из примеров.
5. Если не уверен в тоне - придерживайся более серьезного стиля.
6. Для серьезных тем используй более развернутые ответы в стиле постов из Дзен.

Пиши максимально похоже на стиль из примеров, включая форматирование и эмодзи."""
        
        print(f"Загружено {len(self.messages)} сообщений и постов")
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        await update.message.reply_text(
            'Привет! Я бот, который общается в стиле канала. Я умею шутить и быть серьезным, в зависимости от ситуации. Напиши мне что-нибудь!'
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help"""
        await update.message.reply_text(
            'Я анализирую твои сообщения и отвечаю в подходящем стиле. Если хочешь пошутить - пиши неформально. Для серьезных тем - пиши по делу.'
        )

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик входящих сообщений"""
        user_id = update.effective_user.id
        message_text = update.message.text
        
        # Анализируем тон входящего сообщения
        tone_scores = self.analyze_message_tone(message_text)
        
        try:
            # Получаем историю разговора
            if user_id not in self.conversation_history:
                self.conversation_history[user_id] = []
            
            # Добавляем контекст последних сообщений
            conversation_context = self.conversation_history[user_id][-3:] if self.conversation_history[user_id] else []
            
            messages = [
                {"role": "system", "content": self.system_prompt}
            ]
            
            # Добавляем контекст разговора
            for msg in conversation_context:
                messages.append(msg)
            
            # Добавляем информацию о тоне текущего сообщения
            tone_info = "юмористическом" if tone_scores['humor'] > tone_scores['serious'] else "серьезном"
            messages.append({"role": "user", "content": f"[Сообщение в {tone_info} тоне]: {message_text}"})
            
            # Создаем запрос к OpenAI
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.9,
                max_tokens=1000
            )
            
            reply = response.choices[0].message.content
            
            # Сохраняем сообщения в истории
            self.conversation_history[user_id].append({"role": "user", "content": message_text})
            self.conversation_history[user_id].append({"role": "assistant", "content": reply})
            
            # Ограничиваем историю последними 10 сообщениями
            self.conversation_history[user_id] = self.conversation_history[user_id][-10:]
            
            await update.message.reply_text(reply)
            
        except Exception as e:
            logging.error(f"Ошибка при генерации ответа: {str(e)}")
            await update.message.reply_text("Извините, произошла ошибка при генерации ответа.")

    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик ошибок"""
        logging.error(f"Update {update} caused error {context.error}")

    def run(self):
        """Запускает бота"""
        print("Запуск бота...")
        application = Application.builder().token(self.telegram_token).build()

        # Добавляем обработчики команд
        application.add_handler(CommandHandler('start', self.start_command))
        application.add_handler(CommandHandler('help', self.help_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        application.add_error_handler(self.error_handler)

        # Запускаем бота
        application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    openai_api_key = os.getenv('OPENAI_API_KEY')
    telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not openai_api_key or not telegram_token:
        print("Пожалуйста, укажите OPENAI_API_KEY и TELEGRAM_BOT_TOKEN в файле .env")
    else:
        bot = PersonaBot(openai_api_key, telegram_token)
        # Загружаем сообщения из файла
        telegram_file = "parsed_messages_20250225_011537.txt"
        bot.load_telegram_messages(telegram_file)
        # Запускаем бота
        bot.run()
