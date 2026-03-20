#!/usr/bin/env python3
"""
Telegram Lead Notification Bot
Sends form submissions directly to Telegram
"""

import requests
import json
from datetime import datetime
from pathlib import Path

# Configuration - will be set via environment variables or config file
TELEGRAM_BOT_TOKEN = None  # Set this: export TELEGRAM_BOT_TOKEN="your_token"
TELEGRAM_CHAT_ID = None    # Set this: export TELEGRAM_CHAT_ID="your_chat_id"

LEADS_FILE = Path("/root/.openclaw/workspace/projects/rozlicz/marketing/leads.csv")


def send_telegram_notification(email, source="rozlicz.app", ip=None, user_agent=None):
    """Send lead notification to Telegram"""
    
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Telegram not configured. Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID")
        return False
    
    message = f"""🎉 <b>Nowa rejestracja - Rozlicz.app!</b>

📧 Email: <code>{email}</code>
🌐 Źródło: {source}
⏰ Czas: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    if ip:
        message += f"🌍 IP: {ip}\n"
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.ok:
            print(f"✅ Telegram notification sent for {email}")
            return True
        else:
            print(f"❌ Telegram error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Failed to send Telegram: {e}")
        return False


def save_lead(email, source, consent, ip=None, user_agent=None):
    """Save lead to CSV file"""
    import csv
    
    # Ensure directory exists
    LEADS_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    lead = {
        'timestamp': datetime.now().isoformat(),
        'email': email,
        'source': source,
        'consent': consent,
        'ip': ip or '',
        'user_agent': user_agent or ''
    }
    
    # Write to CSV
    file_exists = LEADS_FILE.exists()
    with open(LEADS_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=lead.keys())
        if not file_exists or f.tell() == 0:
            writer.writeheader()
        writer.writerow(lead)
    
    print(f"✅ Lead saved: {email}")
    return True


def process_lead(email, source="rozlicz.app", consent="true", ip=None, user_agent=None):
    """Process new lead: save + notify"""
    
    # Save to file
    save_lead(email, source, consent, ip, user_agent)
    
    # Send Telegram notification
    send_telegram_notification(email, source, ip, user_agent)
    
    return True


def get_stats():
    """Get lead statistics"""
    import csv
    
    if not LEADS_FILE.exists():
        return {"total": 0, "today": 0, "week": 0}
    
    total = 0
    today = 0
    week = 0
    
    today_str = datetime.now().strftime('%Y-%m-%d')
    week_ago = datetime.now() - timedelta(days=7)
    
    with open(LEADS_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            total += 1
            timestamp = row.get('timestamp', '')
            if timestamp.startswith(today_str):
                today += 1
            try:
                lead_date = datetime.fromisoformat(timestamp)
                if lead_date > week_ago:
                    week += 1
            except:
                pass
    
    return {"total": total, "today": today, "week": week}


if __name__ == '__main__':
    import argparse
    import os
    
    # Load from environment
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
    
    parser = argparse.ArgumentParser(description='Telegram Lead Bot')
    parser.add_argument('--test', help='Send test notification to email')
    parser.add_argument('--stats', action='store_true', help='Show lead statistics')
    
    args = parser.parse_args()
    
    if args.test:
        print(f"Sending test notification for: {args.test}")
        send_telegram_notification(args.test, "test")
    
    elif args.stats:
        stats = get_stats()
        print(f"📊 Lead Statistics:")
        print(f"   Total: {stats['total']}")
        print(f"   Today: {stats['today']}")
        print(f"   This week: {stats['week']}")
    
    else:
        print("Telegram Lead Bot")
        print("Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID environment variables")
        print("\nUsage:")
        print("  --test email@example.com  - Send test notification")
        print("  --stats                    - Show statistics")
