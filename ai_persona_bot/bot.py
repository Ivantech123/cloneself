"""Основной модуль бота."""

import os
import logging
from typing import Dict, Optional
from enum import Enum

import openai
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler

class Voice(str, Enum):
    """Доступные голоса OpenAI TTS."""
    ALLOY = "alloy"  # Нейтральный голос
    ECHO = "echo"    # Глубокий голос
    FABLE = "fable"  # Британский акцент
    ONYX = "onyx"    # Серьезный голос
    NOVA = "nova"    # Мягкий голос
    SHIMMER = "shimmer"  # Оптимистичный голос

class PersonaBot:
    """AI Persona бот с поддержкой голосовых сообщений."""

    def __init__(self, token: str):
        """Инициализация бота.
        
        Args:
            token: Telegram Bot API токен
        """
        self.application = Application.builder().token(token).build()
        self.voice_enabled: Dict[int, bool] = {}
        self.user_voices: Dict[int, Voice] = {}
        
        # Регистрация обработчиков
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("voice", self.voice_command))
        self.application.add_handler(CommandHandler("voice_select", self.voice_select_command))
        self.application.add_handler(CallbackQueryHandler(self.voice_button))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

    async def start_command(self, update: Update, context):
        """Обработка команды /start."""
        await update.message.reply_text(
            "Привет! Я AI Persona бот. Я могу общаться текстом и голосом.\n\n"
            "Команды:\n"
            "/voice - включить/выключить голосовые сообщения\n"
            "/voice_select - выбрать голос"
        )

    async def voice_command(self, update: Update, context):
        """Обработка команды /voice для включения/выключения голосовых сообщений."""
        user_id = update.effective_user.id
        self.voice_enabled[user_id] = not self.voice_enabled.get(user_id, False)
        
        if self.voice_enabled[user_id] and user_id not in self.user_voices:
            self.user_voices[user_id] = Voice.ALLOY
            
        status = "включены" if self.voice_enabled[user_id] else "выключены"
        voice_name = self.user_voices.get(user_id, Voice.ALLOY).value
        
        if self.voice_enabled[user_id]:
            await update.message.reply_text(
                f"Голосовые сообщения {status}\n"
                f"Текущий голос: {voice_name}\n"
                "Используйте /voice_select чтобы выбрать другой голос"
            )
        else:
            await update.message.reply_text(f"Голосовые сообщения {status}")

    async def voice_select_command(self, update: Update, context):
        """Обработка команды /voice_select для выбора голоса."""
        keyboard = []
        for voice in Voice:
            keyboard.append([InlineKeyboardButton(
                f"🎤 {voice.value}" + (" ✓" if self.user_voices.get(update.effective_user.id) == voice else ""),
                callback_data=f"voice_{voice.value}"
            )])
            
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Выберите голос:", reply_markup=reply_markup)

    async def voice_button(self, update: Update, context):
        """Обработка нажатий на кнопки выбора голоса."""
        query = update.callback_query
        await query.answer()
        
        if query.data.startswith("voice_"):
            voice_name = query.data.replace("voice_", "")
            user_id = query.from_user.id
            self.user_voices[user_id] = Voice(voice_name)
            
            # Включаем голосовые сообщения если они были выключены
            if not self.voice_enabled.get(user_id, False):
                self.voice_enabled[user_id] = True
            
            # Обновляем сообщение с кнопками
            keyboard = []
            for voice in Voice:
                keyboard.append([InlineKeyboardButton(
                    f"🎤 {voice.value}" + (" ✓" if voice.value == voice_name else ""),
                    callback_data=f"voice_{voice.value}"
                )])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                f"Выбран голос: {voice_name}\n"
                "Выберите другой голос или отправьте сообщение:",
                reply_markup=reply_markup
            )

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
            voice = self.user_voices.get(user_id, Voice.ALLOY)
            audio_file = self.generate_voice(response, voice)
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

    def generate_voice(self, text: str, voice: Voice = Voice.ALLOY) -> Optional[str]:
        """Генерация голосового сообщения через OpenAI TTS.
        
        Args:
            text: Текст для озвучивания
            voice: Голос для использования (по умолчанию ALLOY)
            
        Returns:
            Путь к аудио файлу или None в случае ошибки
        """
        try:
            response = openai.audio.speech.create(
                model="tts-1",
                voice=voice.value,
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
