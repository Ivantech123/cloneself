"""Основной модуль бота."""

import os
import logging
from typing import Dict, Optional

import openai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

class PersonaBot:
    """AI Persona бот с поддержкой голосовых сообщений."""

    def __init__(self, token: str):
        """Инициализация бота.
        
        Args:
            token: Telegram Bot API токен
        """
        self.application = Application.builder().token(token).build()
        self.voice_enabled: Dict[int, bool] = {}
        
        # Регистрация обработчиков
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("voice", self.voice_command))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

    async def start_command(self, update: Update, context):
        """Обработка команды /start."""
        await update.message.reply_text(
            "Привет! Я AI Persona бот. Я могу общаться текстом и голосом. "
            "Используй /voice чтобы включить/выключить голосовые сообщения."
        )

    async def voice_command(self, update: Update, context):
        """Обработка команды /voice для включения/выключения голосовых сообщений."""
        user_id = update.effective_user.id
        self.voice_enabled[user_id] = not self.voice_enabled.get(user_id, False)
        status = "включены" if self.voice_enabled[user_id] else "выключены"
        await update.message.reply_text(f"Голосовые сообщения {status}")

    async def handle_message(self, update: Update, context):
        """Обработка входящих текстовых сообщений."""
        user_id = update.effective_user.id
        user_message = update.message.text

        # Получаем ответ от OpenAI
        response = self.get_ai_response(user_message)
        
        # Отправляем текстовый ответ
        await update.message.reply_text(response)
        
        # Если включены голосовые сообщения, отправляем и их
        if self.voice_enabled.get(user_id, False):
            audio_file = self.generate_voice(response)
            if audio_file:
                await update.message.reply_voice(audio_file)
                os.remove(audio_file)  # Удаляем временный файл

    def get_ai_response(self, message: str) -> str:
        """Получение ответа от OpenAI API."""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": message}]
            )
            return response.choices[0].message.content
        except Exception as e:
            logging.error(f"Error getting AI response: {e}")
            return "Извините, произошла ошибка при генерации ответа."

    def generate_voice(self, text: str) -> Optional[str]:
        """Генерация голосового сообщения через OpenAI TTS."""
        try:
            response = openai.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=text
            )
            
            # Сохраняем во временный файл
            temp_file = "temp_voice.mp3"
            response.stream_to_file(temp_file)
            return temp_file
        except Exception as e:
            logging.error(f"Error generating voice: {e}")
            return None

    def run(self):
        """Запуск бота."""
        self.application.run_polling()
