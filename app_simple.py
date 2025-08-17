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
from ai_prompts import (
    get_egg_creation_prompt,
    get_image_analysis_prompt,
    get_creature_creation_prompt,
    get_voice_description_prompt,
    get_creature_concept_prompt,
    PHONETIC_SOUNDS,
    CARE_QUESTIONS
)

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

# Essential API endpoints for the app to work
@app.route('/api/analyze-image', methods=['POST'])
@login_required
def analyze_image():
    """API endpoint to analyze an image and generate metadata"""
    try:
        if 'image' in request.files:
            image_file = request.files['image']
            
            # Validate file
            if not image_file or image_file.filename == '':
                return jsonify({
                    "success": False,
                    "message": "No image file provided"
                }), 400
            
            # Check file type
            allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
            file_extension = image_file.filename.rsplit('.', 1)[1].lower() if '.' in image_file.filename else ''
            
            if file_extension not in allowed_extensions:
                return jsonify({
                    "success": False,
                    "message": f"Invalid file type. Allowed types: {', '.join(allowed_extensions)}"
                }), 400
            
            logger.info(f"Processing image: {image_file.filename}")
            
            # For now, return a simple response to test the endpoint
            return jsonify({
                "success": True,
                "analysis": {
                    "description": "Test image analysis - endpoint working!",
                    "descriptors": ["test", "working", "deployment"]
                },
                "message": "Image analysis endpoint is working!"
            })
            
        else:
            return jsonify({
                "success": False,
                "message": "No image file provided"
            }), 400
        
    except Exception as e:
        logger.error(f"API error in analyze_image: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Failed to analyze image"
        }), 500

@app.route('/api/create-egg', methods=['POST'])
@login_required
def create_egg():
    """API endpoint to create an egg from metadata"""
    try:
        data = request.get_json()
        description = data.get('description', '')
        descriptors = data.get('descriptors', [])
        
        if not description or not descriptors:
            return jsonify({
                "success": False,
                "message": "Description and descriptors are required"
            }), 400
        
        # For now, return a simple response to test the endpoint
        return jsonify({
            "success": True,
            "egg": {
                "id": str(uuid.uuid4()),
                "description": description,
                "descriptors": descriptors,
                "image_url": "/static/images/test-egg.png",
                "created_at": datetime.now().isoformat(),
                "status": "created",
                "incubation_stage": 0
            },
            "message": "Egg creation endpoint is working!"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Failed to create egg"
        }), 500

@app.route('/api/care-questions', methods=['GET'])
@login_required
def get_care_questions():
    """Get a single dynamic care question for egg incubation"""
    try:
        import random
        selected_question = random.choice(CARE_QUESTIONS)
        
        questions = {
            "questions": [selected_question]
        }
        
        return jsonify({
            "success": True,
            "questions": questions
        })
        
    except Exception as e:
        logger.error(f"Error getting care questions: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Failed to get care questions"
        }), 500

@app.route('/api/hatch-creature', methods=['POST'])
@login_required
def hatch_creature():
    """Generate a creature based on egg data and care responses"""
    try:
        data = request.get_json()
        egg_id = data.get('egg_id')
        care_responses = data.get('care_responses', {})
        
        if not egg_id:
            return jsonify({
                "success": False,
                "message": "Egg ID is required"
            }), 400
        
        # For now, return a simple response to test the endpoint
        return jsonify({
            "success": True,
            "creature": {
                "id": str(uuid.uuid4()),
                "name": "Test Creature",
                "egg_id": egg_id,
                "image_url": "/static/images/test-creature.png",
                "sound_text": "Test sound",
                "sound_name": "test_sound",
                "voice_description": "A test creature voice",
                "audio_url": None,
                "care_responses": care_responses,
                "hatched_at": datetime.now().isoformat(),
                "egg_traits": ["test", "deployment"],
                "egg_description": "Test egg for deployment"
            },
            "message": "Creature hatching endpoint is working!"
        })
        
    except Exception as e:
        logger.error(f"Error hatching creature: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Failed to hatch creature"
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    logger.info(f"Starting app on port {port}")
    app.run(debug=False, host='0.0.0.0', port=port)
