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

# Load environment variables
load_dotenv()

def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'production')
    
    app = Flask(__name__)
    
    try:
        # Import config after app creation to avoid circular imports
        from config import config
        app.config.from_object(config[config_name])
        config[config_name].init_app(app)
        
        app.secret_key = app.config['SECRET_KEY']
        CORS(app)
        
    except Exception as e:
        # Fallback configuration if config loading fails
        app.secret_key = os.getenv('SECRET_KEY', 'fallback-secret-key')
        CORS(app)
        print(f"Warning: Config loading failed, using fallback: {e}")
    
    return app

# Create the app instance
app = create_app()

# Configure OpenAI
openai.api_key = app.config['OPENAI_API_KEY']

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'authenticated' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        correct_password = app.config['WEBSITE_PASSWORD']
        
        if password == correct_password:
            session['authenticated'] = True
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid password')
    
    return render_template('login.html')

# Logout route
@app.route('/logout')
def logout():
    session.pop('authenticated', None)
    return redirect(url_for('login'))

class EggCreator:
    def __init__(self):
        self.client = openai.OpenAI(api_key=app.config['OPENAI_API_KEY'])
    
    def create_egg_from_metadata(self, description, descriptors):
        """
        Function 1: Creates an egg image from metadata
        Input: description (string) and descriptors (array of strings)
        Output: Generated egg image
        """
        try:
            # Build a detailed prompt for egg creation
            descriptors_text = ", ".join(descriptors)
            prompt = get_egg_creation_prompt(description, descriptors_text)
            
            # Generate image using DALL-E
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            
            # Download and save the image locally
            image_url = response.data[0].url
            logger.info(f"Downloading image from: {image_url}")
            
            image_response = requests.get(image_url)
            image_response.raise_for_status()  # Raise an exception for bad status codes
            
            # Create images directory if it doesn't exist
            os.makedirs("static/images", exist_ok=True)
            
            # Save image with unique filename
            image_filename = f"egg_{str(uuid.uuid4())}.png"
            image_path = os.path.join("static", "images", image_filename)
            
            with open(image_path, 'wb') as f:
                f.write(image_response.content)
            
            logger.info(f"Image saved to: {image_path}")
            
            # Create relative URL for web access
            image_url = f"/static/images/{image_filename}"
            
            # Create egg metadata
            egg_id = str(uuid.uuid4())
            egg_data = {
                "id": egg_id,
                "description": description,
                "descriptors": descriptors,
                "image_url": image_url,
                "created_at": datetime.now().isoformat(),
                "status": "created",
                "incubation_stage": 0
            }
            
            # Save egg data (in a real app, this would go to a database)
            self._save_egg_data(egg_data)
            
            return {
                "success": True,
                "egg": egg_data,
                "message": "Egg created successfully!"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to create egg"
            }
    
    def analyze_image_to_metadata(self, image_data):
        """
        Function 2: Analyzes an image and generates description and metadata
        Input: image (base64 or file)
        Output: description and descriptors for egg creation
        """
        try:
            # Convert image data to base64 if it's a file
            if hasattr(image_data, 'read'):
                # Reset file pointer to beginning
                image_data.seek(0)
                image_bytes = image_data.read()
                image_base64 = base64.b64encode(image_bytes).decode('utf-8')
                
                # Determine image format from file extension or content
                filename = image_data.filename.lower() if hasattr(image_data, 'filename') else ''
                if filename.endswith(('.png', '.PNG')):
                    mime_type = "image/png"
                elif filename.endswith(('.gif', '.GIF')):
                    mime_type = "image/gif"
                elif filename.endswith(('.webp', '.WEBP')):
                    mime_type = "image/webp"
                else:
                    mime_type = "image/jpeg"  # Default to JPEG
            else:
                image_base64 = image_data
                mime_type = "image/jpeg"  # Default to JPEG
            
            # Analyze image with GPT-4 Vision
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": get_image_analysis_prompt()
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500
            )
            
            # Parse the response
            analysis_text = response.choices[0].message.content
            logger.info(f"GPT-4 Vision response: {analysis_text}")
            
            # Try to extract JSON from the response
            try:
                # Find JSON in the response
                start_idx = analysis_text.find('{')
                end_idx = analysis_text.rfind('}') + 1
                if start_idx != -1 and end_idx > start_idx:
                    json_str = analysis_text[start_idx:end_idx]
                    analysis_data = json.loads(json_str)
                else:
                    raise ValueError("No JSON found in response")
            except Exception as json_error:
                logger.error(f"JSON parsing error: {json_error}")
                # Fallback: create structured data from text
                analysis_data = {
                    "description": analysis_text,
                    "descriptors": ["mystical", "unique", "beautiful", "magical"]
                }
            
            return {
                "success": True,
                "analysis": analysis_data,
                "message": "Image analyzed successfully!"
            }
            
        except Exception as e:
            logger.error(f"Image analysis error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to analyze image"
            }
    
    def _save_egg_data(self, egg_data):
        """Save egg data to a simple JSON file (in production, use a database)"""
        try:
            eggs_file = "eggs_data.json"
            eggs = []
            
            if os.path.exists(eggs_file):
                with open(eggs_file, 'r') as f:
                    eggs = json.load(f)
            
            eggs.append(egg_data)
            
            with open(eggs_file, 'w') as f:
                json.dump(eggs, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving egg data: {e}")
    
    def create_creature_from_egg(self, egg, care_responses):
        """
        Generate a unique creature based on egg data and care responses
        """
        try:
            # Build a comprehensive prompt for creature generation
            # Get the single care response (could be any of the question types)
            care_response = list(care_responses.values())[0] if care_responses else 'with love and care'
            care_question_id = list(care_responses.keys())[0] if care_responses else 'general'
            
            # Create context based on the type of question asked
            if care_question_id == 'activities':
                care_context = f"enjoyed activities like {care_response}"
            elif care_question_id == 'feelings':
                care_context = f"made you feel {care_response}"
            elif care_question_id == 'time_spent':
                care_context = f"spent {care_response} together"
            elif care_question_id == 'description':
                care_context = f"described as {care_response}"
            elif care_question_id == 'sounds':
                care_context = f"made sounds like {care_response}"
            elif care_question_id == 'favorite_thing':
                care_context = f"loved for {care_response}"
            elif care_question_id == 'comfort':
                care_context = f"comforted by {care_response}"
            elif care_question_id == 'whispers':
                care_context = f"heard whispers of {care_response}"
            elif care_question_id == 'favorite_spot':
                care_context = f"loved being in {care_response}"
            elif care_question_id == 'celebration':
                care_context = f"celebrated with {care_response}"
            else:
                care_context = f"cared for with {care_response}"
            
            descriptors_text = ", ".join(egg.get('descriptors', []))
            
            # Generate creature concept (name and image prompt) using GPT
            concept_prompt = get_creature_concept_prompt(descriptors_text, care_context)
            
            concept_response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": concept_prompt
                    }
                ],
                max_tokens=300
            )
            
            concept_content = concept_response.choices[0].message.content.strip()
            logger.info(f"Creature concept response: {concept_content}")
            
            # Parse the JSON response to get name and image prompt
            try:
                import json
                import re
                
                # Clean the response content - remove markdown code blocks if present
                cleaned_content = concept_content.strip()
                if cleaned_content.startswith('```json'):
                    # Remove markdown code block formatting
                    cleaned_content = re.sub(r'^```json\s*', '', cleaned_content)
                    cleaned_content = re.sub(r'\s*```$', '', cleaned_content)
                elif cleaned_content.startswith('```'):
                    # Remove generic markdown code block formatting
                    cleaned_content = re.sub(r'^```\s*', '', cleaned_content)
                    cleaned_content = re.sub(r'\s*```$', '', cleaned_content)
                
                concept_data = json.loads(cleaned_content)
                creature_name = concept_data.get('name', 'Unknown')
                image_prompt = concept_data.get('image_prompt', '')
                
                if not image_prompt:
                    # Fallback to original prompt if parsing fails
                    image_prompt = get_creature_creation_prompt(descriptors_text, care_context)
                    logger.warning("Failed to parse image prompt from concept response, using fallback")
                
                logger.info(f"Generated creature name: {creature_name}")
                logger.info(f"Generated image prompt: {image_prompt}")
                
            except (json.JSONDecodeError, KeyError) as e:
                logger.error(f"Error parsing concept response: {e}")
                logger.error(f"Raw response content: {concept_content}")
                # Fallback to original prompt and generate name separately
                image_prompt = get_creature_creation_prompt(descriptors_text, care_context)
                creature_name = "Unknown"
                logger.warning("Using fallback prompts due to parsing error")
            
            # Generate creature image using DALL-E with the dynamic prompt
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=image_prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            
            # Download and save the creature image locally
            creature_image_url = response.data[0].url
            logger.info(f"Downloading creature image from: {creature_image_url}")
            
            creature_image_response = requests.get(creature_image_url)
            creature_image_response.raise_for_status()  # Raise an exception for bad status codes
            
            # Save creature image with unique filename
            creature_image_filename = f"creature_{str(uuid.uuid4())}.png"
            creature_image_path = os.path.join("static", "images", creature_image_filename)
            
            with open(creature_image_path, 'wb') as f:
                f.write(creature_image_response.content)
            
            logger.info(f"Creature image saved to: {creature_image_path}")
            
            # Create relative URL for web access
            creature_image_url = f"/static/images/{creature_image_filename}"
            
            # Generate creature sound using Text-to-Speech
            # Phonetic sound bank for baby creatures - unique single words
            import random
            selected_sound = random.choice(PHONETIC_SOUNDS)
            
            # Generate voice characteristics based on creature traits
            voice_prompt = get_voice_description_prompt(descriptors_text, care_context)
            
            voice_response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": voice_prompt
                    }
                ],
                max_tokens=100
            )
            
            voice_description = voice_response.choices[0].message.content.strip()
            
            # Creature name is already generated from the concept call above
            
            # Generate audio using Text-to-Speech
            try:
                audio_response = self.client.audio.speech.create(
                    model="tts-1",
                    voice="alloy",  # Good for creature-like sounds
                    input=selected_sound
                )
                
                # Create creature ID first for audio filename
                creature_id = str(uuid.uuid4())
                
                # Save audio file
                audio_filename = f"creature_sound_{creature_id}.mp3"
                audio_path = os.path.join("static", "audio", audio_filename)
                
                # Ensure audio directory exists
                os.makedirs(os.path.dirname(audio_path), exist_ok=True)
                
                # Save the audio file
                audio_response.stream_to_file(audio_path)
                
                # Create relative URL for web access
                audio_url = f"/static/audio/{audio_filename}"
                
                sound_data = {
                    "sound_text": selected_sound,
                    "sound_name": f"{selected_sound.lower().replace('!', '').replace(' ', '_')}_sound",
                    "voice_description": voice_description,
                    "audio_url": audio_url
                }
                
            except Exception as audio_error:
                logger.error(f"Audio generation error: {audio_error}")
                sound_data = {
                    "sound_text": selected_sound,
                    "sound_name": f"{selected_sound.lower().replace('!', '').replace(' ', '_')}_sound",
                    "voice_description": voice_description,
                    "audio_url": None
                }
            
            # Create creature data
            creature_data = {
                "id": creature_id,
                "name": creature_name,
                "egg_id": egg.get('id'),
                "image_url": creature_image_url,
                "sound_text": sound_data.get("sound_text", ""),
                "sound_name": sound_data.get("sound_name", ""),
                "voice_description": sound_data.get("voice_description", ""),
                "audio_url": sound_data.get("audio_url", ""),
                "care_responses": care_responses,
                "hatched_at": datetime.now().isoformat(),
                "egg_traits": egg.get('descriptors', []),
                "egg_description": egg.get('description', '')
            }
            
            # Save creature data
            self._save_creature_data(creature_data)
            
            return {
                "success": True,
                "creature": creature_data,
                "message": "Creature hatched successfully!"
            }
            
        except Exception as e:
            logger.error(f"Error creating creature: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to create creature"
            }
    
    def _save_creature_data(self, creature_data):
        """Save creature data to a JSON file"""
        try:
            creatures_file = "creatures_data.json"
            creatures = []
            
            if os.path.exists(creatures_file):
                with open(creatures_file, 'r') as f:
                    creatures = json.load(f)
            
            creatures.append(creature_data)
            
            with open(creatures_file, 'w') as f:
                json.dump(creatures, f, indent=2)
            
            # Update egg status to hatched
            self._update_egg_status(creature_data.get('egg_id'), 'hatched')
                
        except Exception as e:
            logger.error(f"Error saving creature data: {e}")
    
    def _update_egg_status(self, egg_id, status):
        """Update egg status in eggs_data.json"""
        try:
            eggs_file = "eggs_data.json"
            if os.path.exists(eggs_file):
                with open(eggs_file, 'r') as f:
                    eggs = json.load(f)
                
                # Find and update the egg status
                for egg in eggs:
                    if egg['id'] == egg_id:
                        egg['status'] = status
                        break
                
                with open(eggs_file, 'w') as f:
                    json.dump(eggs, f, indent=2)
                    
        except Exception as e:
            logger.error(f"Error updating egg status: {e}")

# Initialize egg creator - will be created when needed
egg_creator = None

def get_egg_creator():
    global egg_creator
    if egg_creator is None:
        egg_creator = EggCreator()
    return egg_creator

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/health')
def health_check():
    """Health check endpoint for deployment verification"""
    return jsonify({
        "status": "healthy",
        "message": "Hatch website is running!",
        "timestamp": datetime.now().isoformat()
    })

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
        
        result = get_egg_creator().create_egg_from_metadata(description, descriptors)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Failed to create egg"
        }), 500

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
            result = get_egg_creator().analyze_image_to_metadata(image_file)
            
        else:
            # Handle JSON data (for base64 images)
            data = request.get_json()
            if not data:
                return jsonify({
                    "success": False,
                    "message": "No image data provided"
                }), 400
            
            image_data = data.get('image_data', '')
            if not image_data:
                return jsonify({
                    "success": False,
                    "message": "No image_data in request"
                }), 400
            
            result = get_egg_creator().analyze_image_to_metadata(image_data)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"API error in analyze_image: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Failed to analyze image"
        }), 500

@app.route('/api/eggs', methods=['GET'])
@login_required
def get_eggs():
    """Get all created eggs"""
    try:
        eggs_file = "eggs_data.json"
        if os.path.exists(eggs_file):
            with open(eggs_file, 'r') as f:
                eggs = json.load(f)
            return jsonify({
                "success": True,
                "eggs": eggs
            })
        else:
            return jsonify({
                "success": True,
                "eggs": []
            })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Failed to retrieve eggs"
        }), 500

@app.route('/api/creatures', methods=['GET'])
@login_required
def get_creatures():
    """Get all hatched creatures"""
    try:
        creatures_file = "creatures_data.json"
        if os.path.exists(creatures_file):
            with open(creatures_file, 'r') as f:
                creatures = json.load(f)
            return jsonify({
                "success": True,
                "creatures": creatures
            })
        else:
            return jsonify({
                "success": True,
                "creatures": []
            })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Failed to retrieve creatures"
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
        
        # Get egg data
        eggs_file = "eggs_data.json"
        if not os.path.exists(eggs_file):
            return jsonify({
                "success": False,
                "message": "Egg not found"
            }), 404
        
        with open(eggs_file, 'r') as f:
            eggs = json.load(f)
        
        egg = next((e for e in eggs if e['id'] == egg_id), None)
        if not egg:
            return jsonify({
                "success": False,
                "message": "Egg not found"
            }), 404
        
        # Generate creature using the egg creator
        result = get_egg_creator().create_creature_from_egg(egg, care_responses)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error hatching creature: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Failed to hatch creature"
        }), 500

@app.route('/static/audio/<filename>')
@login_required
def serve_audio(filename):
    """Serve audio files with proper headers"""
    try:
        audio_path = os.path.join("static", "audio", filename)
        if os.path.exists(audio_path):
            return send_file(audio_path, mimetype='audio/mpeg')
        else:
            return jsonify({"error": "Audio file not found"}), 404
    except Exception as e:
        logger.error(f"Error serving audio: {str(e)}")
        return jsonify({"error": "Failed to serve audio"}), 500

@app.route('/static/images/<filename>')
@login_required
def serve_image(filename):
    """Serve image files"""
    try:
        image_path = os.path.join("static", "images", filename)
        if os.path.exists(image_path):
            return send_file(image_path)
        else:
            return jsonify({"error": "Image file not found"}), 404
    except Exception as e:
        logger.error(f"Error serving image: {str(e)}")
        return jsonify({"error": "Failed to serve image"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=True, host='0.0.0.0', port=port) 