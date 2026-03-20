#!/usr/bin/env python3
"""
Email Automation System for Rozlicz.app
Automated email sequences for new leads
"""

import json
import smtplib
import csv
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
import time

# Configuration
LEADS_FILE = Path("/root/.openclaw/workspace/projects/rozlicz/marketing/leads.csv")
SEQUENCE_FILE = Path("/root/.openclaw/workspace/projects/rozlicz/marketing/email_sequences.json")
SENT_LOG = Path("/root/.openclaw/workspace/projects/rozlicz/marketing/sent_emails.json")

# Email templates
EMAIL_TEMPLATES = {
    "welcome": {
        "subject": "Witaj w Rozlicz.app! Twój darmowy okres próbny",
        "body": """Cześć!

Dziękujemy za zainteresowanie Rozlicz.app!

Jesteśmy w trakcie przygotowywania systemu do premiery. W ciągu 24h skontaktuje się z Tobą nasz ekspert, aby:

✓ Omówić Twoje potrzeby księgowe
✓ Pokazać, jak działa automatyzacja KSeF
✓ Aktywować 7-dniowy darmowy okres próbny

Co możesz zrobić już teraz:
→ Sprawdź jak wygląda dashboard: https://rozlicz.app#dashboard
→ Przeczytaj FAQ: https://rozlicz.app#faq

Masz pytania? Odpowiedz na ten email lub napisz na kontakt@rozlicz.app

Do zobaczenia!
Zespół Rozlicz.app
"""
    },
    
    "day3_reminder": {
        "subject": "Czekamy na Ciebie - Rozlicz.app",
        "body": """Cześć!

Minęły 3 dni od Twojej rejestracji w Rozlicz.app.

Czy miałeś/aś już okazję przemyśleć swoje potrzeby księgowe?

Przypominamy, że oferujemy:
• 7 dni darmowego okresu próbnego
• Automatyczny import faktur z KSeF
• Stałą cenę 400 zł netto bez limitu faktur
• Gwarancję niekaralności

Chętnie odpowiemy na wszystkie pytania - wystarczy odpowiedzieć na ten email.

Pozdrawiamy,
Zespół Rozlicz.app
"""
    },
    
    "day7_last_chance": {
        "subject": "Ostatnia szansa - wersja beta Rozlicz.app",
        "body": """Cześć!

To już tydzień od Twojej rejestracji.

Przygotowujemy się do właściwego startu i chcielibyśmy, żebyś był/a wśród pierwszych użytkowników.

Jako jeden z pierwszych 50 klientów otrzymasz:
✓ Stałą cenę 400 zł netto (nawet gdy cena wzrośnie)
✓ Priorytetowe wsparcie techniczne
✓ Wpływ na rozwój funkcji

Nie przegap okazji - odpowiedz na ten email, aby aktywować dostęp.

Pozdrawiamy,
Zespół Rozlicz.app
"""
    }
}

class EmailAutomation:
    """Automated email sequences"""
    
    def __init__(self, smtp_config=None):
        self.smtp_config = smtp_config or {}
        self.load_sent_log()
    
    def load_sent_log(self):
        """Load log of sent emails"""
        if SENT_LOG.exists():
            with open(SENT_LOG, 'r') as f:
                self.sent = json.load(f)
        else:
            self.sent = {}
    
    def save_sent_log(self):
        """Save log of sent emails"""
        with open(SENT_LOG, 'w') as f:
            json.dump(self.sent, f, indent=2)
    
    def get_new_leads(self):
        """Get leads from CSV"""
        leads = []
        if LEADS_FILE.exists():
            with open(LEADS_FILE, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    leads.append(row)
        return leads
    
    def should_send(self, email, template_name):
        """Check if email should be sent"""
        key = f"{email}:{template_name}"
        return key not in self.sent
    
    def mark_sent(self, email, template_name):
        """Mark email as sent"""
        key = f"{email}:{template_name}"
        self.sent[key] = datetime.now().isoformat()
        self.save_sent_log()
    
    def send_email(self, to_email, template_name):
        """Send email using template"""
        if not self.should_send(to_email, template_name):
            print(f"⏭️  Already sent {template_name} to {to_email}")
            return False
        
        template = EMAIL_TEMPLATES.get(template_name)
        if not template:
            print(f"❌ Template {template_name} not found")
            return False
        
        # For now, just log (SMTP not configured)
        print(f"📧 Would send '{template['subject']}' to {to_email}")
        print(f"   Body preview: {template['body'][:100]}...")
        
        # Uncomment when SMTP is configured:
        # msg = MIMEMultipart()
        # msg['From'] = self.smtp_config.get('from', 'kontakt@rozlicz.app')
        # msg['To'] = to_email
        # msg['Subject'] = template['subject']
        # msg.attach(MIMEText(template['body'], 'plain', 'utf-8'))
        # 
        # with smtplib.SMTP(self.smtp_config['host'], self.smtp_config['port']) as server:
        #     server.starttls()
        #     server.login(self.smtp_config['user'], self.smtp_config['pass'])
        #     server.send_message(msg)
        
        self.mark_sent(to_email, template_name)
        return True
    
    def process_sequences(self):
        """Process all email sequences"""
        leads = self.get_new_leads()
        now = datetime.now()
        
        sent_count = 0
        
        for lead in leads:
            email = lead.get('email')
            timestamp = lead.get('timestamp')
            
            if not email or not timestamp:
                continue
            
            try:
                lead_time = datetime.fromisoformat(timestamp)
                hours_since = (now - lead_time).total_seconds() / 3600
                
                # Welcome email - immediately
                if hours_since < 1 and self.should_send(email, 'welcome'):
                    if self.send_email(email, 'welcome'):
                        sent_count += 1
                
                # Day 3 reminder
                elif 72 <= hours_since < 73 and self.should_send(email, 'day3_reminder'):
                    if self.send_email(email, 'day3_reminder'):
                        sent_count += 1
                
                # Day 7 last chance
                elif 168 <= hours_since < 169 and self.should_send(email, 'day7_last_chance'):
                    if self.send_email(email, 'day7_last_chance'):
                        sent_count += 1
                        
            except Exception as e:
                print(f"❌ Error processing {email}: {e}")
        
        print(f"\n📊 Total emails sent: {sent_count}")
        return sent_count
    
    def preview_sequences(self, email):
        """Preview what emails would be sent to a lead"""
        print(f"\n📧 Email sequence preview for: {email}")
        print("=" * 60)
        
        for name, template in EMAIL_TEMPLATES.items():
            status = "✅ Would send" if self.should_send(email, name) else "⏭️ Already sent"
            print(f"\n{name}:")
            print(f"  Subject: {template['subject']}")
            print(f"  Status: {status}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Rozlicz Email Automation')
    parser.add_argument('--run', action='store_true', help='Run email sequences')
    parser.add_argument('--preview', help='Preview sequences for email')
    parser.add_argument('--list', action='store_true', help='List all leads')
    
    args = parser.parse_args()
    
    automation = EmailAutomation()
    
    if args.run:
        print("🚀 Running email sequences...")
        automation.process_sequences()
    
    elif args.preview:
        automation.preview_sequences(args.preview)
    
    elif args.list:
        leads = automation.get_new_leads()
        print(f"\n📊 Total leads: {len(leads)}")
        for lead in leads[-10:]:  # Last 10
            print(f"  {lead.get('timestamp', 'N/A')[:10]} | {lead.get('email', 'N/A')}")
    
    else:
        # Default: show status
        leads = automation.get_new_leads()
        print(f"📊 Leads in database: {len(leads)}")
        print(f"📧 Emails sent: {len(automation.sent)}")
        print(f"\nTemplates available: {', '.join(EMAIL_TEMPLATES.keys())}")
        print("\nRun with --run to process sequences")


if __name__ == '__main__':
    main()
