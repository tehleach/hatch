from flask import Flask, request, jsonify, render_template, send_file, session, redirect, url_for
from flask_cors import CORS
import openai
import os
import base64
import io
from PIL import Image
import json
from dotenv import load_dotenv
import uuid
from datetime import datetime
import logging
import requests
from functools import wraps

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('hatch.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Basic configuration
app.secret_key = os.getenv('SECRET_KEY', 'fallback-secret-key-change-this')
app.config['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')
app.config['WEBSITE_PASSWORD'] = os.getenv('WEBSITE_PASSWORD', 'hatch123')

# Enable CORS
CORS(app)

# Configure OpenAI
if app.config['OPENAI_API_KEY']:
    openai.api_key = app.config['OPENAI_API_KEY']
    logger.info("OpenAI API key configured")
else:
    logger.warning("No OpenAI API key found")

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'authenticated' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Health check endpoint (no auth required)
@app.route('/health')
def health_check():
    """Health check endpoint for deployment verification"""
    return jsonify({
        "status": "healthy",
        "message": "Hatch website is running!",
        "timestamp": datetime.now().isoformat(),
        "openai_configured": bool(app.config.get('OPENAI_API_KEY')),
        "password_configured": bool(app.config.get('WEBSITE_PASSWORD'))
    })

# Root endpoint (no auth required for testing)
@app.route('/')
def index():
    return jsonify({
        "message": "Hatch website is running!",
        "endpoints": {
            "health": "/health",
            "login": "/login",
            "main_app": "/app"
        }
    })

# Main app endpoint (requires auth)
@app.route('/app')
@login_required
def main_app():
    return render_template('index.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        correct_password = app.config['WEBSITE_PASSWORD']
        
        if password == correct_password:
            session['authenticated'] = True
            return redirect(url_for('main_app'))
        else:
            return render_template('login.html', error='Invalid password')
    
    return render_template('login.html')

# Logout route
@app.route('/logout')
def logout():
    session.pop('authenticated', None)
    return redirect(url_for('login'))

# Basic API endpoint for testing
@app.route('/api/test')
def test_api():
    return jsonify({
        "success": True,
        "message": "API is working!",
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    logger.info(f"Starting app on port {port}")
    app.run(debug=False, host='0.0.0.0', port=port)
