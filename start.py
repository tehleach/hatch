#!/usr/bin/env python3
"""
Start script for Hatch - AI Egg Creation & Incubation System
"""

import os
import sys
import subprocess
from dotenv import load_dotenv

def main():
    print("🥚 Welcome to Hatch - AI Egg Creation & Incubation System!")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ No .env file found!")
        print("   Please create a .env file with your OpenAI API key:")
        print("   OPENAI_API_KEY=your_actual_api_key_here")
        print("\n   You can copy from env.example as a starting point.")
        return 1
    
    # Check API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key or api_key == "your_openai_api_key_here":
        print("❌ Invalid OpenAI API key in .env file")
        print("   Please set a valid OPENAI_API_KEY in your .env file")
        return 1
    
    # Check dependencies
    try:
        import flask
        import openai
        import PIL
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("   Please run: pip install -r requirements.txt")
        return 1
    
    print("✅ Environment check passed!")
    print("\n🚀 Starting Hatch server...")
    print("   Open your browser to: http://localhost:5001")
    print("   Press Ctrl+C to stop the server")
    print("-" * 60)
    
    # Start the Flask app
    try:
        subprocess.run([sys.executable, "app.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Thanks for using Hatch!")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error starting server: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 