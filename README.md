🎙️ Telegram Voice Bot

AI-powered Telegram bot for voice message transcription, summarization, and task extraction. Supports Russian language with automatic speaker detection.

✨ Features





🎵 Voice Message Transcription - Convert voice messages to text using OpenAI Whisper



👥 Speaker Detection - Automatic identification of different speakers in conversations



📊 Smart Summarization - Generate organized summaries by roles/speakers



✅ Task Extraction - Automatically extract tasks and action items



📝 Full Transcript - Format complete transcriptions with timestamps



📈 Text Statistics - Detailed analysis of transcribed content

🛠️ Tech Stack





Backend: FastAPI + Python 3.9+



Bot Framework: aiogram 3.x



AI Services: OpenAI Whisper + GPT-4o-mini



Deployment: Docker-ready with webhook support

📁 Project Structure

voicebot/
├── app/
│   ├── main.py              # FastAPI entry point with webhook
│   ├── telegram_bot.py      # Bot logic and message handlers
│   ├── transcriber.py       # Audio-to-text conversion
│   ├── summarizer.py        # AI text processing
│   └── config.py           # Configuration and environment variables
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
├── .gitignore             # Git ignore rules
└── README.md              # This file


🚀 Quick Start

1. Prerequisites





Python 3.9+



Telegram Bot Token (from @BotFather)



OpenAI API Key (from OpenAI Platform)

2. Local Setup

# Clone repository
git clone <repository-url>
cd voicebot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your credentials
nano .env


3. Environment Variables

Create .env file with the following variables:

# Telegram Bot Configuration
BOT_TOKEN=your_telegram_bot_token_here
WEBHOOK_URL=https://yourdomain.com/webhook

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Optional Configuration
CHAT_MODEL=gpt-4o-mini
TRANSCRIPTION_MODEL=whisper-1
TEMPERATURE=0.2
MAX_AUDIO_SIZE_MB=20
MAX_TEXT_LENGTH=4000
APP_HOST=0.0.0.0
PORT=8000


4. Development Mode (Local Testing)

# Run with polling (no webhook needed)
cd app
python main.py dev


5. Production Mode (Webhook)

# Run with webhook
cd app
python main.py
# or
uvicorn main:app --host 0.0.0.0 --port 8000


🌐 Deployment Options

Option 1: Railway (Recommended)







Connect GitHub Repository





Fork this repository



Connect your Railway account to GitHub



Select the forked repository



Configure Environment Variables

BOT_TOKEN=your_bot_token
WEBHOOK_URL=https://yourapp.railway.app/webhook
OPENAI_API_KEY=your_openai_key




Deploy Settings





Build Command: pip install -r requirements.txt



Start Command: cd app && python -m uvicorn main:app --host 0.0.0.0 --port $PORT

Option 2: Render





Connect Repository





Go to Render Dashboard



Create new Web Service from GitHub repository



Build Settings





Build Command: pip install -r requirements.txt



Start Command: cd app && python -m uvicorn main:app --host 0.0.0.0 --port $PORT



Environment Variables

BOT_TOKEN=your_bot_token
WEBHOOK_URL=https://yourapp.onrender.com/webhook
OPENAI_API_KEY=your_openai_key


Option 3: Heroku





Create Heroku App

heroku create your-voice-bot
heroku config:set BOT_TOKEN=your_bot_token
heroku config:set WEBHOOK_URL=https://your-voice-bot.herokuapp.com/webhook
heroku config:set OPENAI_API_KEY=your_openai_key




Create Procfile

web: cd app && python -m uvicorn main:app --host 0.0.0.0 --port $PORT




Deploy

git push heroku main


Option 4: PythonAnywhere





Upload Files





Upload project files to your PythonAnywhere account



Extract to /home/yourusername/voicebot/



Create Web App





Go to Web tab → Add a new web app



Choose "Manual configuration" and Python 3.9



Configure WSGI

# In /var/www/yourusername_pythonanywhere_com_wsgi.py
import sys
import os

path = '/home/yourusername/voicebot'
if path not in sys.path:
    sys.path.append(path)

os.chdir('/home/yourusername/voicebot/app')

from main import app
application = app


Option 5: Docker





Create Dockerfile

FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app/ ./app/

EXPOSE 8000
CMD ["python", "app/main.py"]




Build and Run

docker build -t voice-bot .
docker run -p 8000:8000 --env-file .env voice-bot


🔧 Configuration

Bot Commands





/start - Welcome message and instructions



/help - Usage help and feature list



/stats - User session statistics

Webhook Endpoints





GET / - Bot status and information



POST /webhook - Telegram webhook endpoint



GET /health - Health check for load balancers



GET /ping - Keep-alive endpoint



GET /bot-info - Bot information



GET /webhook-info - Webhook status

Audio Limits





Maximum file size: 20 MB (configurable)



Supported formats: OGG, MP3, WAV



Language: Russian (optimized)

Text Processing Limits





Maximum text length: 4000 characters (configurable)



Response limit: 1500 tokens per AI request



Telegram message limit: 4096 characters (auto-split)

🎯 Usage





Start the bot - Send /start command



Send voice message - Record and send any voice message



Wait for transcription - Bot will process and transcribe audio



Choose action - Select from available options:





📊 General Summary - Key points organized by speakers



📝 Full Text - Complete transcription with speaker markers



✅ Extract Tasks - Action items and assignments



📈 Statistics - Text analysis and metrics

⚠️ Free Hosting Considerations

Sleep Mode Prevention

Many free hosting platforms put apps to sleep after inactivity. Solutions:





Use monitoring services:





UptimeRobot - Free monitoring



Pingdom - Uptime monitoring



Configure keep-alive:

# Add to cron or use external service to ping every 25 minutes
curl https://yourapp.com/ping




Choose platforms without sleep:





Railway (recommended)



Fly.io



DigitalOcean App Platform

Resource Limits

Free tier limitations:





RAM: 512MB - 1GB



CPU: Limited/shared



Storage: 1GB - 5GB



Bandwidth: 100GB/month

Optimize for free hosting:





Use environment variables for configuration



Implement proper error handling



Add request timeouts



Use efficient audio processing

🔍 Monitoring & Debugging

Check Bot Status

# Health check
curl https://yourapp.com/health

# Bot information
curl https://yourapp.com/bot-info

# Webhook status
curl https://yourapp.com/webhook-info


Common Issues





Webhook not working





Check WEBHOOK_URL in environment variables



Ensure URL uses HTTPS



Verify bot token is correct



OpenAI API errors





Check API key validity



Monitor usage limits



Verify model names



Audio processing fails





Check file size limits



Verify supported formats



Monitor OpenAI Whisper quota

Logs

Application logs include:





Request processing



Error details



API usage statistics



Performance metrics

💰 Cost Estimation

OpenAI API Costs (approximate)





Whisper: $0.006 per minute of audio



GPT-4o-mini: $0.15 per 1M input tokens, $0.60 per 1M output tokens

Example monthly costs:





100 voice messages (2 min each): ~$1.20



300 voice messages (2 min each): ~$3.60



Processing & summaries: ~$2-5/month

🛡️ Security Best Practices





Environment Variables





Never commit API keys to version control



Use secure environment variable storage



Rotate keys regularly



Input Validation





File size limits implemented



Content type verification



Rate limiting recommended



Error Handling





Graceful failure handling



No sensitive data in error messages



Comprehensive logging

🤝 Contributing





Fork the repository



Create feature branch (git checkout -b feature/amazing-feature)



Commit changes (git commit -m 'Add amazing feature')



Push to branch (git push origin feature/amazing-feature)



Open Pull Request

📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

🆘 Support





Issues: GitHub Issues



Telegram: Contact bot developer



Documentation: This README

🔮 Roadmap





Multi-language support



Advanced speaker diarization



Integration with task management tools



Voice message replies



Audio file upload support



Custom AI model options



Group chat support



Conversation context memory



Made with ❤️ using Python, FastAPI, and OpenAI