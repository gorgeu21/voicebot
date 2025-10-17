"""
Configuration module for Telegram Voice Bot
Loads environment variables and provides configuration settings
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Telegram Bot Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is required")

# Webhook Configuration
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
if not WEBHOOK_URL:
    raise ValueError("WEBHOOK_URL environment variable is required")

# OpenRouter API Configuration (Primary)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
OPENROUTER_APP_NAME = os.getenv("OPENROUTER_APP_NAME", "TelegramVoiceBot")
OPENROUTER_SITE_URL = os.getenv("OPENROUTER_SITE_URL", "https://github.com/user/telegram-voice-bot")

# OpenAI Configuration (Fallback)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
USE_OPENAI_FALLBACK = os.getenv("USE_OPENAI_FALLBACK", "true").lower() == "true"

# Validate API keys
if not OPENROUTER_API_KEY and not OPENAI_API_KEY:
    raise ValueError("Either OPENROUTER_API_KEY or OPENAI_API_KEY must be provided")

if not OPENROUTER_API_KEY and not USE_OPENAI_FALLBACK:
    raise ValueError("OPENROUTER_API_KEY is required when fallback is disabled")

# Application Configuration
APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("PORT", "8000"))  # Railway, Render use PORT env var

# Audio Processing Configuration
MAX_AUDIO_SIZE_MB = int(os.getenv("MAX_AUDIO_SIZE_MB", "20"))  # 20MB default
MAX_TEXT_LENGTH = int(os.getenv("MAX_TEXT_LENGTH", "4000"))  # 4000 chars default

# Model Configuration
# For transcription - keep Whisper through OpenAI for now (OpenRouter doesn't have reliable Whisper support)
TRANSCRIPTION_MODEL = os.getenv("TRANSCRIPTION_MODEL", "whisper-1")
TRANSCRIPTION_PROVIDER = os.getenv("TRANSCRIPTION_PROVIDER", "openai")  # openai or openrouter

# For chat completion - use OpenRouter models
CHAT_MODEL = os.getenv("CHAT_MODEL", "openai/gpt-4o-mini")  # OpenRouter format
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.2"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1500"))

# Request timeout and retry configuration
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))  # seconds
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
RETRY_DELAY = float(os.getenv("RETRY_DELAY", "1.0"))  # seconds

# Webhook validation
if WEBHOOK_URL and not WEBHOOK_URL.startswith("https://"):
    raise ValueError("WEBHOOK_URL must use HTTPS protocol")

print(f"✅ Configuration loaded successfully")
print(f"📍 Webhook URL: {WEBHOOK_URL}")
print(f"🤖 Chat Model: {CHAT_MODEL}")
print(f"🎤 Transcription Model: {TRANSCRIPTION_MODEL}")
