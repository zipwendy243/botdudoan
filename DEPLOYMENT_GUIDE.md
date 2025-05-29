# Nova88 Telegram Bot - aaPanel Deployment Guide

## Prerequisites

1. aaPanel server with Python 3.11+ installed
2. PostgreSQL database setup
3. Required API keys:
   - Telegram Bot Token
   - OpenAI API Key

## Step-by-Step Deployment Instructions

### 1. Prepare Your Server

1. Log into your aaPanel
2. Go to **App Store** → **Python Manager** → Install Python 3.11
3. Go to **Database** → **PostgreSQL** → Create a new database for the bot

### 2. Upload Project Files

1. Create a new directory in your server: `/www/wwwroot/nova88_bot/`
2. Upload all these files to that directory:
   - `app.py`
   - `main.py`
   - `bot_handler.py`
   - `prediction_service.py`
   - `slot_game_service.py`
   - `language_service.py`
   - `pgsoft_scraper.py`
   - `models.py`
   - `wsgi.py`
   - `config.py`
   - `deployment_requirements.txt`
   - `translations_*.json` (all 4 files)
   - `user_languages.json`

### 3. Install Dependencies

SSH into your server and run:
```bash
cd /www/wwwroot/nova88_bot/
pip3 install -r deployment_requirements.txt
```

### 4. Set Environment Variables

Create a `.env` file in your project directory:
```bash
nano .env
```

Add these variables (replace with your actual values):
```
DATABASE_URL=postgresql://username:password@localhost:5432/nova88_bot
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
OPENAI_API_KEY=your_openai_api_key_here
SESSION_SECRET=your_random_secret_key_here
WEBHOOK_URL=https://yourdomain.com
PORT=5000
FLASK_ENV=production
```

### 5. Configure aaPanel Website

1. In aaPanel, go to **Website** → **Add site**
2. Domain: your domain name
3. Root directory: `/www/wwwroot/nova88_bot/`
4. PHP Version: Select **Python 3.11**

### 6. Configure Python Application

1. Go to **Website** → Select your site → **Python**
2. Set these configurations:
   - **Startup File**: `wsgi.py`
   - **Application Root**: `/www/wwwroot/nova88_bot/`
   - **Port**: 5000

### 7. Set Up SSL Certificate

1. Go to **Website** → Select your site → **SSL**
2. Enable SSL and configure your certificate
3. Force HTTPS redirect

### 8. Configure Nginx (if needed)

Add this to your Nginx configuration:
```nginx
location / {
    proxy_pass http://127.0.0.1:5000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

### 9. Initialize Database

SSH into your server and run:
```bash
cd /www/wwwroot/nova88_bot/
python3 -c "from app import app, db; app.app_context().push(); db.create_all()"
```

### 10. Set Telegram Webhook

1. Start your application
2. Visit: `https://yourdomain.com/test` to verify it's running
3. The webhook will be automatically set when the bot starts

### 11. Configure Process Manager

1. In aaPanel, go to **Process Manager**
2. Add a new process:
   - **Name**: Nova88 Bot
   - **Directory**: `/www/wwwroot/nova88_bot/`
   - **Command**: `gunicorn --bind 0.0.0.0:5000 --workers 2 wsgi:app`

### 12. Test Your Bot

1. Message your bot on Telegram with `/start`
2. Test lottery predictions with `/du_doan`
3. Test slot games with `/ds_slot`

## Troubleshooting

### Common Issues:

1. **Database Connection Error**
   - Verify PostgreSQL is running
   - Check DATABASE_URL format
   - Ensure database exists

2. **Telegram Webhook Issues**
   - Verify TELEGRAM_BOT_TOKEN is correct
   - Ensure SSL certificate is valid
   - Check WEBHOOK_URL matches your domain

3. **OpenAI API Errors**
   - Verify OPENAI_API_KEY is valid
   - Check API quotas and billing

4. **Permission Issues**
   - Set proper file permissions: `chmod 755 /www/wwwroot/nova88_bot/`
   - Ensure www-data user has access

## Monitoring

1. Check logs in aaPanel → **Logs**
2. Monitor process status in **Process Manager**
3. Set up monitoring alerts for your application

## Security Notes

1. Keep your `.env` file secure
2. Regular security updates
3. Monitor API usage
4. Use strong database passwords
5. Enable firewall rules

## Maintenance

1. Regular backups of database
2. Monitor disk space
3. Update dependencies periodically
4. Monitor API usage and costs