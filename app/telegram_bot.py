"""
Telegram bot logic and message handlers
Handles voice messages, user interactions, and bot commands
"""
import logging
from typing import Dict, Any
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import BOT_TOKEN
from transcriber import transcribe_voice_message
from summarizer import generate_summary, extract_action_items, format_transcript

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# In-memory storage for user sessions (in production, use Redis or database)
user_sessions: Dict[int, Dict[str, Any]] = {}

# Maximum message length for Telegram (4096 characters)
MAX_MESSAGE_LENGTH = 4000

def split_long_message(text: str, max_length: int = MAX_MESSAGE_LENGTH) -> list:
    """Split long message into chunks that fit Telegram's limit"""
    if len(text) <= max_length:
        return [text]
    
    chunks = []
    current_chunk = ""
    
    for line in text.split('\n'):
        if len(current_chunk) + len(line) + 1 <= max_length:
            current_chunk += line + '\n'
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = line + '\n'
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

def create_action_buttons() -> InlineKeyboardMarkup:
    """Create inline keyboard with action buttons"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text="📊 Общая сводка (по ролям)",
            callback_data="action_summary"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="📝 Полный текст (по ролям)",
            callback_data="action_fulltext"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="✅ Выделить задачи",
            callback_data="action_tasks"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="📈 Статистика",
            callback_data="action_stats"
        )
    )
    
    return builder.as_markup()

def create_processing_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard shown during processing"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="⏳ Обработка...",
            callback_data="processing"
        )
    )
    return builder.as_markup()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Handle /start command"""
    welcome_text = """🎙️ **Добро пожаловать в Voice Bot!**

Я умею:
• 🎵 Распознавать голосовые сообщения
• 📊 Создавать сводки по ролям
• ✅ Выделять задачи и действия
• 📝 Форматировать полный текст

**Как пользоваться:**
1. Отправьте голосовое сообщение
2. Дождитесь распознавания
3. Выберите нужное действие

Поддерживаю русский язык и автоматическое определение говорящих.

*Отправьте голосовое сообщение, чтобы начать!*"""
    
    await message.answer(welcome_text, parse_mode="Markdown")

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    """Handle /help command"""
    help_text = """❓ **Справка по использованию**

**Команды:**
• `/start` - Приветствие и инструкции
• `/help` - Эта справка
• `/stats` - Статистика вашей сессии

**Функции:**
• **Общая сводка** - Краткий обзор ключевых моментов
• **Полный текст** - Вся транскрипция с маркерами говорящих
• **Выделить задачи** - Список действий и поручений
• **Статистика** - Информация о тексте

**Ограничения:**
• Максимальный размер аудио: 20 МБ
• Поддерживаемые форматы: OGG, MP3, WAV
• Язык распознавания: Русский

**Поддержка:** Если что-то не работает, попробуйте переотправить сообщение."""
    
    await message.answer(help_text, parse_mode="Markdown")

@dp.message(Command("stats"))
async def cmd_stats(message: types.Message):
    """Handle /stats command"""
    user_id = message.from_user.id
    session = user_sessions.get(user_id, {})
    
    stats_text = f"""📊 **Статистика вашей сессии**

• Обработано сообщений: {session.get('messages_processed', 0)}
• Последняя активность: {session.get('last_activity', 'Не определена')}
• Статус: {'Есть активная транскрипция' if session.get('current_text') else 'Нет активной транскрипции'}

*Отправьте голосовое сообщение для анализа!*"""
    
    await message.answer(stats_text, parse_mode="Markdown")

@dp.message(types.ContentType.VOICE)
async def handle_voice(message: types.Message):
    """Handle voice messages"""
    user_id = message.from_user.id
    
    try:
        # Send processing message
        processing_msg = await message.reply(
            "🎙️ **Обрабатываю голосовое сообщение...**\n\n⏳ Транскрибирую аудио...",
            parse_mode="Markdown",
            reply_markup=create_processing_keyboard()
        )
        
        # Get voice file info
        voice = message.voice
        logger.info(f"Received voice message: duration={voice.duration}s, size={voice.file_size} bytes")
        
        # Download voice file
        file = await bot.get_file(voice.file_id)
        file_bytes = await bot.download_file(file.file_path)
        
        # Update processing message
        await processing_msg.edit_text(
            "🎙️ **Обрабатываю голосовое сообщение...**\n\n🔍 Распознаю речь...",
            parse_mode="Markdown",
            reply_markup=create_processing_keyboard()
        )
        
        # Transcribe audio
        transcription_result = await transcribe_voice_message(file_bytes, f"voice_{voice.file_id}.ogg")
        
        if not transcription_result["success"]:
            error_text = f"❌ **Ошибка транскрипции:**\n\n{transcription_result.get('error', 'Неизвестная ошибка')}"
            await processing_msg.edit_text(error_text, parse_mode="Markdown")
            return
        
        # Store transcription in user session
        if user_id not in user_sessions:
            user_sessions[user_id] = {}
        
        user_sessions[user_id].update({
            'current_text': transcription_result['processed_text'],
            'raw_text': transcription_result['text'],
            'last_activity': message.date.strftime("%Y-%m-%d %H:%M:%S"),
            'messages_processed': user_sessions[user_id].get('messages_processed', 0) + 1,
            'duration': transcription_result.get('duration', 0),
            'segments': transcription_result.get('segments', [])
        })
        
        # Success message with action buttons
        success_text = f"""✅ **Голосовое сообщение распознано!**

📊 **Информация:**
• Длительность: {voice.duration} сек.
• Размер: {round(voice.file_size / 1024, 1)} КБ
• Символов в тексте: {len(transcription_result['processed_text'])}

**Выберите действие:**"""
        
        await processing_msg.edit_text(
            success_text,
            parse_mode="Markdown",
            reply_markup=create_action_buttons()
        )
        
        logger.info(f"Voice message processed successfully for user {user_id}")
        
    except Exception as e:
        logger.error(f"Error processing voice message: {str(e)}")
        await processing_msg.edit_text(
            f"❌ **Произошла ошибка:**\n\n{str(e)}\n\n*Попробуйте отправить сообщение еще раз.*",
            parse_mode="Markdown"
        )

@dp.callback_query()
async def handle_callback(callback: types.CallbackQuery):
    """Handle inline button callbacks"""
    user_id = callback.from_user.id
    action = callback.data
    
    # Ignore processing button clicks
    if action == "processing":
        await callback.answer("Обработка в процессе...")
        return
    
    # Get user session
    session = user_sessions.get(user_id)
    if not session or not session.get('current_text'):
        await callback.answer("❌ Не найдена транскрипция. Отправьте голосовое сообщение.", show_alert=True)
        return
    
    try:
        # Show processing
        await callback.message.edit_text(
            f"⏳ **Выполняю действие...**\n\n🔄 Обрабатываю текст...",
            parse_mode="Markdown"
        )
        
        text = session['current_text']
        
        if action == "action_summary":
            # Generate summary
            result = await generate_summary(text)
            
            if result["success"]:
                response_text = f"📊 **ОБЩАЯ СВОДКА**\n\n{result['content']}"
                action_name = "Сводка готова!"
            else:
                response_text = f"❌ **Ошибка генерации сводки:**\n\n{result.get('error', 'Неизвестная ошибка')}"
                action_name = "Ошибка сводки"
                
        elif action == "action_fulltext":
            # Format full text
            result = await format_transcript(text)
            
            if result["success"]:
                response_text = result['content']
                action_name = "Полный текст готов!"
            else:
                response_text = f"❌ **Ошибка форматирования:**\n\n{result.get('error', 'Неизвестная ошибка')}"
                action_name = "Ошибка форматирования"
                
        elif action == "action_tasks":
            # Extract tasks
            result = await extract_action_items(text)
            
            if result["success"]:
                response_text = result['content']
                action_name = "Задачи извлечены!"
            else:
                response_text = f"❌ **Ошибка извлечения задач:**\n\n{result.get('error', 'Неизвестная ошибка')}"
                action_name = "Ошибка извлечения задач"
                
        elif action == "action_stats":
            # Show text statistics
            from summarizer import processor
            stats = processor.get_text_stats(text)
            
            response_text = f"""📈 **СТАТИСТИКА ТЕКСТА**

📊 **Основные показатели:**
• Символов: {stats['characters']:,}
• Слов: {stats['words']:,}
• Строк: {stats['lines']:,}
• Говорящих: {stats['speakers_detected']}
• Время чтения: ~{stats['estimated_reading_time']} мин.

🔧 **Технические:**
• В пределах лимита: {'✅ Да' if stats['within_limits'] else '❌ Нет'}
• Длительность аудио: {session.get('duration', 0):.1f} сек.
• Сегментов: {len(session.get('segments', []))}"""
            
            action_name = "Статистика готова!"
        else:
            response_text = "❌ Неизвестное действие"
            action_name = "Ошибка"
        
        # Split long messages
        message_chunks = split_long_message(response_text)
        
        # Send first chunk as edit, others as new messages
        await callback.message.edit_text(
            message_chunks[0],
            parse_mode="Markdown",
            reply_markup=create_action_buttons()
        )
        
        # Send additional chunks if needed
        for chunk in message_chunks[1:]:
            await callback.message.reply(chunk, parse_mode="Markdown")
        
        await callback.answer(action_name)
        
        logger.info(f"Action {action} completed for user {user_id}")
        
    except Exception as e:
        logger.error(f"Error handling callback {action}: {str(e)}")
        await callback.message.edit_text(
            f"❌ **Произошла ошибка при выполнении действия:**\n\n{str(e)}",
            parse_mode="Markdown",
            reply_markup=create_action_buttons()
        )
        await callback.answer("Произошла ошибка")

@dp.message()
async def handle_other_messages(message: types.Message):
    """Handle all other messages"""
    await message.reply(
        "🎙️ Отправьте голосовое сообщение для обработки.\n\n"
        "Используйте /help для получения справки.",
        parse_mode="Markdown"
    )

# Error handler
@dp.error()
async def error_handler(event, exception):
    """Global error handler"""
    logger.error(f"Bot error: {exception}")
    return True

# Export bot and dispatcher for main.py
__all__ = ['bot', 'dp']
