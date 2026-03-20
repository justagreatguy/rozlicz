#!/usr/bin/env python3
"""
Rozlicz Lead API + Telegram Notifications
Simple Flask app for collecting leads
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from telegram_bot import process_lead, get_stats, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

app = Flask(__name__)

# Enable CORS for all domains (for GitHub Pages)
CORS(app, resources={
    r"/api/*": {
        "origins": ["*"],  # Allow all origins for now
        "methods": ["POST", "GET", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

@app.route('/api/lead', methods=['POST'])
def collect_lead():
    """Receive lead from website form"""
    try:
        # Parse JSON or form data
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
        
        # Process lead
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        user_agent = request.headers.get('User-Agent', '')[:200]
        
        process_lead(email, source, consent, ip, user_agent)
        
        return jsonify({
            'success': True,
            'message': 'Dziękujemy! Sprawdź email, wysłaliśmy potwierdzenie.'
        })
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/stats', methods=['GET'])
def api_stats():
    """Get lead statistics"""
    try:
        stats = get_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'telegram_configured': bool(TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID),
        'version': '1.0'
    })


@app.route('/', methods=['GET'])
def index():
    """Root endpoint"""
    return jsonify({
        'service': 'Rozlicz Lead API',
        'endpoints': {
            '/api/lead': 'POST - Submit new lead',
            '/api/stats': 'GET - Get statistics',
            '/api/health': 'GET - Health check'
        }
    })


if __name__ == '__main__':
    # Check configuration
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️  Warning: Telegram not configured!")
        print("   Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID environment variables")
        print("   Leads will still be saved to CSV file.\n")
    
    port = int(os.getenv('PORT', 5000))
    print(f"🚀 Starting Lead API on port {port}")
    print(f"   Endpoints:")
    print(f"   - POST http://localhost:{port}/api/lead")
    print(f"   - GET  http://localhost:{port}/api/stats")
    print(f"   - GET  http://localhost:{port}/api/health\n")
    
    app.run(host='0.0.0.0', port=port, debug=False)
