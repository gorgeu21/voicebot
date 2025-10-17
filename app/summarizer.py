"""
Text processing module using OpenRouter API for summarization and task extraction
Handles summary generation, task extraction, and text analysis with fallback support
"""
import logging
from typing import Dict, Any
from openrouter_client import create_chat_completion
from config import CHAT_MODEL, TEMPERATURE, MAX_TEXT_LENGTH, MAX_TOKENS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TextProcessor:
    """Handles text processing using OpenAI GPT models"""
    
    def __init__(self):
        self.max_text_length = MAX_TEXT_LENGTH
        self.model = CHAT_MODEL
        self.temperature = TEMPERATURE
    
    def _truncate_text(self, text: str) -> str:
        """Truncate text if it exceeds maximum length"""
        if len(text) <= self.max_text_length:
            return text
        
        truncated = text[:self.max_text_length - 100]  # Leave space for truncation message
        return f"{truncated}\n\n[ТЕКСТ ОБРЕЗАН - СЛИШКОМ ДЛИННЫЙ]"
    
    async def _call_ai_api(self, prompt: str, system_message: str = None) -> Dict[str, Any]:
        """
        Make a call to OpenRouter API with fallback support
        
        Args:
            prompt: User prompt to send
            system_message: Optional system message
            
        Returns:
            Dictionary with response or error
        """
        try:
            messages = []
            
            if system_message:
                messages.append({"role": "system", "content": system_message})
            
            messages.append({"role": "user", "content": prompt})
            
            # Call OpenRouter API with fallback
            response = await create_chat_completion(
                messages=messages,
                model=self.model,
                temperature=self.temperature,
                max_tokens=MAX_TOKENS
            )
            
            if response["success"]:
                return {
                    "success": True,
                    "content": response["content"],
                    "model": response.get("model", self.model),
                    "provider": response.get("provider", "unknown"),
                    "tokens_used": response.get("tokens_used", 0),
                    "input_tokens": response.get("input_tokens", 0),
                    "output_tokens": response.get("output_tokens", 0)
                }
            else:
                return {
                    "success": False,
                    "error": response.get("error", "Unknown API error"),
                    "content": "",
                    "provider": response.get("provider", "unknown")
                }
            
        except Exception as e:
            logger.error(f"AI API call failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "content": "",
                "provider": "unknown"
            }
    
    async def generate_summary_by_roles(self, text: str) -> Dict[str, Any]:
        """
        Generate a summary of the text organized by speakers/roles
        
        Args:
            text: Transcribed text with speaker markers
            
        Returns:
            Dictionary with summary results
        """
        truncated_text = self._truncate_text(text)
        
        system_message = """Ты — помощник для анализа транскрибированных голосовых сообщений. 
Твоя задача — создавать краткие, структурированные сводки."""
        
        prompt = f"""Вот транскрибированный текст голосового сообщения с маркировкой говорящих:

{truncated_text}

Создай краткую ОБЩУЮ СВОДКУ, которая включает:
1. Ключевые моменты и темы обсуждения
2. Основные договорённости или решения
3. Важные выводы
4. Вклад каждого говорящего

Организуй сводку по ролям/говорящим, если в тексте несколько участников.
Будь кратким, но информативным. Максимум 300 слов."""
        
        logger.info(f"Generating summary for text of {len(text)} characters")
        
        result = await self._call_openai(prompt, system_message)
        
        if result["success"]:
            logger.info("Summary generated successfully")
        
        return result
    
    async def extract_tasks(self, text: str) -> Dict[str, Any]:
        """
        Extract tasks and action items from the text
        
        Args:
            text: Transcribed text with speaker markers
            
        Returns:
            Dictionary with extracted tasks
        """
        truncated_text = self._truncate_text(text)
        
        system_message = """Ты — помощник для извлечения задач и действий из текста. 
Ты должен находить конкретные, выполнимые задачи."""
        
        prompt = f"""Вот транскрибированный текст голосового сообщения:

{truncated_text}

Извлеки из текста ВСЕ ЗАДАЧИ И ДЕЙСТВИЯ, которые нужно выполнить:

Формат ответа:
📋 **ЗАДАЧИ И ДЕЙСТВИЯ:**

• **[Исполнитель]** - Описание задачи
• **[Исполнитель]** - Описание задачи
...

Если исполнитель не указан явно, используй **[Не указан]**.
Если задач нет, напиши: "❌ Конкретных задач в сообщении не обнаружено."

Ищи:
- Прямые поручения ("сделай", "подготовь", "отправь")
- Обязательства ("я сделаю", "мне нужно")
- Планы ("нужно", "необходимо", "следует")
- Дедлайны и временные рамки"""
        
        logger.info(f"Extracting tasks from text of {len(text)} characters")
        
        result = await self._call_openai(prompt, system_message)
        
        if result["success"]:
            logger.info("Tasks extracted successfully")
        
        return result
    
    async def format_full_text(self, text: str) -> Dict[str, Any]:
        """
        Format the full transcribed text for better readability
        
        Args:
            text: Transcribed text with speaker markers
            
        Returns:
            Dictionary with formatted text
        """
        try:
            # Simple formatting - add headers and clean up
            formatted_text = f"""📝 **ПОЛНАЯ ТРАНСКРИПЦИЯ**

{text}

---
💡 *Транскрибировано с помощью AI. Возможны неточности.*"""
            
            return {
                "success": True,
                "content": formatted_text,
                "original_length": len(text),
                "formatted_length": len(formatted_text)
            }
            
        except Exception as e:
            logger.error(f"Text formatting failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "content": text
            }
    
    def get_text_stats(self, text: str) -> Dict[str, Any]:
        """
        Get statistics about the text
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with text statistics
        """
        words = text.split()
        lines = text.split('\n')
        
        return {
            "characters": len(text),
            "words": len(words),
            "lines": len(lines),
            "within_limits": len(text) <= self.max_text_length,
            "speakers_detected": text.count("**Говорящий"),
            "estimated_reading_time": max(1, len(words) // 200)  # ~200 words per minute
        }

# Global processor instance
processor = TextProcessor()

# Convenience functions
async def generate_summary(text: str) -> Dict[str, Any]:
    """Generate summary by roles"""
    return await processor.generate_summary_by_roles(text)

async def extract_action_items(text: str) -> Dict[str, Any]:
    """Extract tasks and action items"""
    return await processor.extract_tasks(text)

async def format_transcript(text: str) -> Dict[str, Any]:
    """Format full transcript"""
    return await processor.format_full_text(text)
