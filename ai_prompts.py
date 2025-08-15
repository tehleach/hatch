"""
AI Prompts for the Hatch Application

This file contains all the AI prompts used throughout the application,
centralized for easy editing and maintenance.

USAGE:
- Import the specific prompt functions you need: 
  from ai_prompts import get_egg_creation_prompt, get_creature_creation_prompt
  
- Call the functions with required parameters:
  prompt = get_egg_creation_prompt(description, descriptors_text)

MODIFYING PROMPTS:
- Edit the prompt text directly in the function return statements
- Test changes by running the application
- All prompts are automatically used when the functions are called

PROMPT CATEGORIES:
1. Egg Creation: Prompts for generating egg images from metadata
2. Image Analysis: Prompts for analyzing uploaded images
3. Creature Creation: Prompts for generating creature images and characteristics
4. Phonetic Sounds: Array of creature sound words
5. Care Questions: Questions asked during egg incubation

TIPS:
- Keep prompts clear and specific
- Test with different inputs to ensure robustness
- Consider adding more negative prompts for image generation if needed
- Voice and name prompts should be concise for better AI responses
"""

# ============================================================================
# EGG CREATION PROMPTS
# ============================================================================

def get_egg_creation_prompt(description: str, descriptors_text: str) -> str:
    """Generate the prompt for creating egg images from metadata"""
    return f"""
    Create a beautiful, mystical egg that represents the following:
    
    Description: {description}
    Descriptors: {descriptors_text}
    
    The egg should be:
    - In a 2D Japanese anime inspired style (see below)
    - Visually stunning and detailed
    - Mystical and magical in appearance
    - Unique and one-of-a-kind
    - Suitable for a creature that will hatch from it
    - Against an aesthetically pleasing background that doesn't distract from the egg
    
    Style: A whimsical, emotionally resonant 2D animation style characterized by soft, painterly environments and clean-lined character design. It blends naturalistic scenery with a gentle sense of fantasy, emphasizing warmth, nostalgia, and childlike wonder. Characters are designed with rounded, approachable forms and expressive features, using a simplified but charming aesthetic. The color palette is vibrant but balanced, often evoking seasonal atmospheres. Lighting is natural and gentle, contributing to a dreamlike but grounded mood. The overall tone is optimistic, quiet, and heartfelt, suitable for adventures rooted in connection with nature, community, and magical realism.
    """

# ============================================================================
# IMAGE ANALYSIS PROMPTS
# ============================================================================

def get_image_analysis_prompt() -> str:
    """Generate the prompt for analyzing images to create egg metadata"""
    return """
    Analyze this image and provide:
    1. A detailed description of an egg inspired by what you see (focus on visual elements, colors, textures, patterns). The egg should not directly recreate the image, it should capture the spirit and aesthetics of the image.
    2. A list of 5-8 descriptive keywords/traits that capture the essence of this image
    
    Format your response as JSON with these keys:
    - description: (string)
    - descriptors: (array of strings)
    """

# ============================================================================
# CREATURE CREATION PROMPTS
# ============================================================================

def get_creature_concept_prompt(descriptors_text: str, care_context: str) -> str:
    """Generate the prompt for creating a creature concept with name and image prompt"""
    return f"""
    Create a creature and then name and generate a prompt that I can use to create a pixel art sprite of it using dall-e. 
    The dall-e prompt should be a fully copy-paste ready prompt that describes a simple 40x40 pixel sprite of the creature. Make sure the prompt leads with "40x40 pixel art sprite of" and keep the description relatively short, no more than 16 words.

    Subject:
    - Cute, fantastical infant inspired by {descriptors_text}
    - Personality reflects {care_context}
    - Surprising, delightful, unexpected details

    Style:
    - Pixel art style consisting of a 40x40 pixel image

    Return JSON with these keys: name: (name), image_prompt: (image_prompt).
    """

def get_creature_creation_prompt(descriptors_text: str, care_context: str) -> str:
    """Generate the prompt for creating creature images from egg data and care responses"""
    return f"""
    Full-body portrait of a newborn magical creature — absolutely NO text, letters, numbers, captions, watermarks, or logos.

    Subject:
    - Cute, fantastical infant inspired by → {descriptors_text}
    - Personality reflects → {care_context}
    - Surprising, delightful design details

    Style:
    - 2-D Japanese anime–inspired illustration
    - Whimsical, emotionally resonant

    Composition:
    - Single subject, centered, isolated on a plain soft background
    - No environment, props, patterns, or particles

    Negative prompt: text, lettering, type, logo, caption, watermark, signature, calligraphy, symbols, glyphs
    """

def get_voice_description_prompt(descriptors_text: str, care_context: str) -> str:
    """Generate the prompt for describing creature voice characteristics"""
    return f"""
    Based on this creature's characteristics, describe the voice qualities for a baby creature sound:
    
    EGG TRAITS: {descriptors_text}
    CARE CONTEXT: {care_context}
    
    Describe the voice in 1-2 sentences, focusing on:
    - Pitch (high/low)
    - Speed (fast/slow)
    - Emotion (happy/sleepy/excited/curious)
    - Quality (soft/harsh/melodic/whispery)
    
    Keep it brief and focused on voice characteristics.
    """



# ============================================================================
# PHONETIC SOUNDS
# ============================================================================

PHONETIC_SOUNDS = [
    "rawr",
    "raaahh",
    "mreow", 
    "wulf",
    "chirp",
    "purr",
    "squeak",
    "giggle",
    "woof",
    "meow",
    "tweet",
    "grr",
    "peep",
    "mur",
    "yip",
    "coo",
    "snuffle",
    "waddle",
    "bounce",
    "wiggle",
    "sparkle",
    "glow",
    "whisper",
    "blorp",
    "floop",
    "zorp",
    "grwar",
    "yeeeep",
    "yaaaa",
    "meeiiii",
    "quat",
    "keekee",
    "prupru"
]

# ============================================================================
# CARE QUESTIONS
# ============================================================================

CARE_QUESTIONS = [
    {
        "id": "activities",
        "question": "What activities do you do with the egg?",
        "placeholder": "e.g., sing lullabies, read stories, gentle rocking..."
    },
    {
        "id": "feelings",
        "question": "How does the egg make you feel?",
        "placeholder": "e.g., peaceful, excited, protective, curious..."
    },
    {
        "id": "time_spent",
        "question": "How much time did you spend daily with the egg?",
        "placeholder": "e.g., all day, just mornings, whenever I pass by..."
    },
    {
        "id": "description",
        "question": "What's a word you would use to describe the egg?",
        "placeholder": "e.g., magical, peaceful, mysterious, precious..."
    },
    {
        "id": "sounds",
        "question": "What sounds do you think the egg makes?",
        "placeholder": "e.g., gentle humming, soft whispers, quiet rustling..."
    },
    {
        "id": "favorite_thing",
        "question": "What's your favorite thing about the egg?",
        "placeholder": "e.g., its colors, the way it glows, its patterns..."
    },
    {
        "id": "comfort",
        "question": "How do you comfort the egg when it seems restless?",
        "placeholder": "e.g., gentle touches, soft words, warm blankets..."
    },
    {
        "id": "whispers",
        "question": "What do you whisper to the egg?",
        "placeholder": "e.g., secrets, hopes, dreams, encouragement..."
    },
    {
        "id": "favorite_spot",
        "question": "What's the egg's favorite spot in your home?",
        "placeholder": "e.g., by the window, near the fireplace, in the garden..."
    },
    {
        "id": "celebration",
        "question": "How do you celebrate the egg's progress?",
        "placeholder": "e.g., special treats, decorations, songs, dances..."
    }
] 