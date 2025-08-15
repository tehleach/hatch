# Hatch - AI Egg Creation & Incubation System

A magical AI-driven prototype for creating, incubating, and hatching dynamic creatures. This system uses OpenAI's APIs to generate mystical eggs from descriptions and analyze images to create egg metadata.

## Features

### 🥚 Egg Creation
- **Text-to-Egg**: Create beautiful, mystical eggs from text descriptions and descriptors
- **Image Analysis**: Upload images to generate egg descriptions and metadata
- **AI-Powered**: Uses gpt 4o for image generation and GPT-4 Vision for image analysis

### 🎨 Beautiful Interface
- **Mystical Design**: Dark theme with animated gradients and magical aesthetics
- **Responsive**: Works on desktop and mobile devices
- **Interactive**: Smooth animations and intuitive user experience

### 📱 Three Main Functions
1. **Create Egg**: Input description and descriptors to generate an egg image
2. **Analyze Image**: Upload an image to get description and metadata for egg creation
3. **Collection**: View all your created eggs in a beautiful gallery

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- OpenAI API key

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd hatch
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```bash
   OPENAI_API_KEY=your_openai_api_key_here
   WEBSITE_PASSWORD=hatch123
   SECRET_KEY=your-secret-key-change-this-in-production
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open your browser**
   Navigate to `http://localhost:5001`
6. **Enter the password** when prompted (default: `hatch123`)

## Authentication

The website is protected with a simple password system. Set the `WEBSITE_PASSWORD` environment variable to change the default password (`hatch123`).

**Security Note**: This is lightweight authentication suitable for personal use. For production deployments, consider implementing more robust authentication methods.

## API Endpoints

### Create Egg
- **POST** `/api/create-egg`
- **Body**: `{"description": "string", "descriptors": ["array", "of", "strings"]}`
- **Returns**: Generated egg with image URL and metadata

### Analyze Image
- **POST** `/api/analyze-image`
- **Body**: Form data with image file
- **Returns**: Analysis with description, descriptors, and creature suggestions

### Get Eggs
- **GET** `/api/eggs`
- **Returns**: Array of all created eggs

## Core Functions

### 1. `create_egg_from_metadata(description, descriptors)`
Creates an egg image using gpt 4o based on:
- **description**: Detailed text description of the desired egg
- **descriptors**: Array of keywords/traits for the egg

### 2. `analyze_image_to_metadata(image_data)`
Analyzes an uploaded image using GPT-4 Vision to extract:
- **description**: Detailed visual description
- **descriptors**: Relevant keywords and traits

## Project Structure

```
hatch/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── .env                  # Environment variables (create this)
├── eggs_data.json        # Egg storage (auto-generated)
├── templates/
│   └── index.html        # Main web interface
└── static/
    ├── css/
    │   └── style.css     # Beautiful mystical styling
    └── js/
        └── app.js        # Frontend functionality
```

## Usage Examples

### Creating an Egg
1. Go to the "Create Egg" tab
2. Enter a description like: "A crystalline egg with swirling aurora patterns that pulse with inner light"
3. Add descriptors: "mystical, crystalline, aurora, ethereal, ancient"
4. Click "Create Egg" and watch the magic happen!

### Analyzing an Image
1. Go to the "Analyze Image" tab
2. Upload any image (nature, art, objects, etc.)
3. The AI will analyze it and suggest egg characteristics
4. Use the analysis to create a new egg

## Technical Details

- **Backend**: Flask with OpenAI API integration
- **Frontend**: Vanilla JavaScript with modern CSS
- **Image Generation**: gpt 4o for high-quality egg images
- **Image Analysis**: GPT-4 Vision for intelligent image understanding
- **Storage**: Simple JSON file (can be upgraded to database)

## Future Enhancements

- [ ] Egg incubation system with time-based progression
- [ ] Creature hatching and interaction
- [ ] Voice/chat interaction with creatures
- [ ] Database integration for persistent storage
- [ ] User accounts and collections
- [ ] Social features and egg sharing
- [ ] Advanced creature evolution system

## Contributing

This is a prototype project. Feel free to fork and enhance it with additional features!

## License

MIT License - feel free to use this project for learning and experimentation.

---

**Note**: This project requires an OpenAI API key with access to gpt 4o and GPT-4 Vision models. Make sure your API key has the necessary permissions and credits. 