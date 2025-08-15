#!/bin/bash

echo "🚀 Preparing to deploy Hatch website..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    echo "Please create a .env file with your configuration:"
    echo "cp env.example .env"
    echo "Then edit .env with your actual values"
    exit 1
fi

# Check if git is initialized
if [ ! -d .git ]; then
    echo "📁 Initializing git repository..."
    git init
    git add .
    git commit -m "Initial commit"
    echo "✅ Git repository initialized"
else
    echo "📁 Git repository already exists"
fi

# Check if remote origin is set
if ! git remote get-url origin > /dev/null 2>&1; then
    echo "🔗 Please set your GitHub repository as remote origin:"
    echo "git remote add origin https://github.com/yourusername/your-repo-name.git"
    echo "Then run this script again"
    exit 1
fi

# Show current status
echo "📊 Current git status:"
git status --short

# Ask user if they want to commit and push
read -p "Do you want to commit and push changes? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "💾 Committing changes..."
    git add .
    read -p "Enter commit message: " commit_msg
    git commit -m "${commit_msg:-Update website}"
    
    echo "🚀 Pushing to GitHub..."
    git push origin main
    
    echo "✅ Code pushed to GitHub!"
    echo ""
    echo "🎯 Next steps:"
    echo "1. Go to https://render.com"
    echo "2. Create a new Web Service"
    echo "3. Connect your GitHub repository"
    echo "4. Set environment variables from your .env file"
    echo "5. Deploy!"
    echo ""
    echo "📖 See DEPLOYMENT.md for detailed instructions"
else
    echo "❌ Deployment cancelled"
fi
