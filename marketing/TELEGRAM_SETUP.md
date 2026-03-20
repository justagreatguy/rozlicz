# Telegram Bot Setup for Lead Notifications

## Why Telegram?
- ✅ Completely FREE, no limits
- ✅ Instant notifications on your phone
- ✅ No email spam filters
- ✅ Simple setup

## Setup Steps

### 1. Create Telegram Bot (2 minutes)

1. Open Telegram and search for **@BotFather**
2. Start chat and send: `/newbot`
3. Choose name: `Rozlicz Leads`
4. Choose username: `rozllicz_leads_bot` (must end in _bot)
5. **Copy the API token** (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 2. Get Your Chat ID (1 minute)

1. Search for **@userinfobot** in Telegram
2. Start chat
3. It will show your ID (e.g., `123456789`)
4. **Copy the ID**

### 3. Test the Bot

```bash
cd marketing
export TELEGRAM_BOT_TOKEN="your_token_here"
export TELEGRAM_CHAT_ID="your_chat_id"

# Test notification
python3 telegram_bot.py --test test@example.com
```

### 4. Run Lead API Server

```bash
# Install dependencies
pip3 install -r requirements.txt

# Run server
export TELEGRAM_BOT_TOKEN="your_token_here"
export TELEGRAM_CHAT_ID="your_chat_id"
python3 lead_api.py
```

Server will start on `http://localhost:5000`

### 5. Deploy (Options)

#### Option A: Local Server (if you have public IP)
```bash
# Run with public access
export TELEGRAM_BOT_TOKEN="..."
export TELEGRAM_CHAT_ID="..."
python3 lead_api.py

# Update index.html API_URL to your IP
```

#### Option B: Render.com (FREE, recommended)
1. Go to https://render.com
2. Create new Web Service
3. Connect your GitHub repo
4. Set environment variables:
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
5. Deploy (free tier: always on)

#### Option C: Railway.app (FREE)
Similar to Render, free tier available.

### 6. Update Website

After deploying API, update `index.html`:

```javascript
const API_URL = 'https://your-api-url.com/api/lead';  // Your deployed URL
```

## How It Works

1. User submits form on rozlicz.app
2. JavaScript sends POST to your API
3. API saves lead to `leads.csv`
4. API sends Telegram notification
5. You get instant message on phone

## Email Funnel (Coming Next)

Once leads are collected, run email automation:

```bash
# Setup cron job to run every hour
0 * * * * cd /path/to/marketing && python3 email_automation.py --run
```

This will send:
- Welcome email immediately
- Day 3 reminder
- Day 7 last chance

## Files

- `telegram_bot.py` - Telegram notifications
- `lead_api.py` - Flask API server
- `email_automation.py` - Email sequences
- `leads.csv` - Lead database
