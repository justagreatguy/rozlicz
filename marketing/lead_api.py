#!/usr/bin/env python3
"""
Rozlicz Lead API - Simple CSV Storage
No notifications, just saves to Excel/CSV file
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import csv
import json
from datetime import datetime
from pathlib import Path

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": ["*"],
        "methods": ["POST", "GET", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Storage file
LEADS_FILE = Path("/root/.openclaw/workspace/projects/rozlicz/marketing/leads.csv")
LEADS_FILE.parent.mkdir(parents=True, exist_ok=True)


def save_lead(email, source, consent, ip=None, user_agent=None):
    """Save lead to CSV file"""
    lead = {
        'timestamp': datetime.now().isoformat(),
        'email': email,
        'source': source,
        'consent': consent,
        'ip': ip or '',
        'user_agent': user_agent or ''
    }
    
    file_exists = LEADS_FILE.exists()
    with open(LEADS_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=lead.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(lead)
    
    print(f"✅ Lead saved: {email}")
    return True


def get_stats():
    """Get lead statistics"""
    if not LEADS_FILE.exists():
        return {"total": 0, "today": 0, "week": 0}
    
    total = 0
    today = 0
    week = 0
    
    today_str = datetime.now().strftime('%Y-%m-%d')
    week_ago = datetime.now() - __import__('datetime').timedelta(days=7)
    
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


@app.route('/api/lead', methods=['POST'])
def collect_lead():
    """Receive lead from website form"""
    try:
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
        
        email = data.get('email', '').strip().lower()
        source = data.get('source', 'rozlicz.app')
        consent = data.get('consent', 'false')
        
        # Validation
        if not email or '@' not in email:
            return jsonify({'error': 'Invalid email'}), 400
        
        if consent != 'true':
            return jsonify({'error': 'Consent required'}), 400
        
        # Get client info
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        user_agent = request.headers.get('User-Agent', '')[:200]
        
        # Save lead
        save_lead(email, source, consent, ip, user_agent)
        
        return jsonify({
            'success': True,
            'message': 'Dziękujemy! Skontaktujemy się w ciągu 24h.'
        })
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/leads', methods=['GET'])
def get_leads():
    """Get all leads (for admin review)"""
    try:
        if not LEADS_FILE.exists():
            return jsonify({'count': 0, 'leads': []})
        
        leads = []
        with open(LEADS_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                leads.append(row)
        
        return jsonify({
            'count': len(leads),
            'leads': leads[-50:]  # Last 50 only
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/stats', methods=['GET'])
def api_stats():
    """Get lead statistics"""
    return jsonify(get_stats())


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'leads_file': str(LEADS_FILE),
        'file_exists': LEADS_FILE.exists()
    })


@app.route('/', methods=['GET'])
def index():
    """Root"""
    return jsonify({
        'service': 'Rozlicz Lead API',
        'storage': 'CSV file (leads.csv)',
        'endpoints': {
            'POST /api/lead': 'Submit new lead',
            'GET /api/leads': 'View all leads',
            'GET /api/stats': 'Statistics',
            'GET /api/health': 'Health check'
        }
    })


if __name__ == '__main__':
    import os
    port = int(os.getenv('PORT', 5000))
    
    print(f"🚀 Lead API starting on port {port}")
    print(f"📁 Leads saved to: {LEADS_FILE}")
    print(f"🔗 Test: curl -X POST http://localhost:{port}/api/lead \\")
    print(f"   -H 'Content-Type: application/json' \\")
    print(f"   -d '{{\"email\":\"test@example.com\",\"consent\":\"true\"}}'")
    
    app.run(host='0.0.0.0', port=port, debug=False)
