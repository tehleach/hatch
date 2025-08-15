#!/usr/bin/env python3
"""
Simple test script to verify the Hatch setup
"""

import os
import sys
from dotenv import load_dotenv

def test_environment():
    """Test if environment variables are set up correctly"""
    print("🔍 Testing Hatch Environment Setup...")
    
    # Load environment variables
    load_dotenv()
    
    # Check OpenAI API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment variables")
        print("   Please create a .env file with your OpenAI API key")
        print("   Example: OPENAI_API_KEY=your_api_key_here")
        return False
    elif api_key == "your_openai_api_key_here":
        print("❌ Please replace the placeholder API key with your actual OpenAI API key")
        return False
    else:
        print("✅ OPENAI_API_KEY found")
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {python_version.major}.{python_version.minor}")
        return False
    else:
        print(f"✅ Python version {python_version.major}.{python_version.minor} is compatible")
    
    # Check if required packages can be imported
    try:
        import flask
        print("✅ Flask is available")
    except ImportError:
        print("❌ Flask not found. Run: pip install -r requirements.txt")
        return False
    
    try:
        import openai
        print("✅ OpenAI package is available")
    except ImportError:
        print("❌ OpenAI package not found. Run: pip install -r requirements.txt")
        return False
    
    try:
        import PIL
        print("✅ Pillow (PIL) is available")
    except ImportError:
        print("❌ Pillow not found. Run: pip install -r requirements.txt")
        return False
    
    print("\n🎉 Environment setup looks good!")
    print("   You can now run: python app.py")
    return True

if __name__ == "__main__":
    success = test_environment()
    sys.exit(0 if success else 1) 