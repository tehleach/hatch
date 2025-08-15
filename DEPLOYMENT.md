# Deploying Your Hatch Website to the Internet

This guide will help you deploy your creature hatching website to Render, a free hosting platform.

## Prerequisites

1. **GitHub Account**: You'll need to push your code to GitHub first
2. **Render Account**: Sign up at [render.com](https://render.com) (free)
3. **OpenAI API Key**: Make sure you have your OpenAI API key ready

## Step 1: Prepare Your Code for GitHub

1. **Create a .env file** (this will NOT be uploaded to GitHub):
   ```bash
   cp env.example .env
   ```
   
2. **Edit .env with your actual values**:
   ```bash
   OPENAI_API_KEY=your_actual_openai_api_key_here
   WEBSITE_PASSWORD=your_chosen_password
   SECRET_KEY=your_long_random_secret_key_here
   FLASK_ENV=production
   FLASK_DEBUG=False
   ```

3. **Generate a secure SECRET_KEY**:
   ```bash
   python3 -c "import secrets; print(secrets.token_hex(32))"
   ```

## Step 2: Push to GitHub

1. **Initialize git repository** (if not already done):
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```

2. **Create a new repository on GitHub** and push your code:
   ```bash
   git remote add origin https://github.com/yourusername/your-repo-name.git
   git branch -M main
   git push -u origin main
   ```

## Step 3: Deploy on Render

1. **Go to [render.com](https://render.com)** and sign up/login

2. **Click "New +" and select "Web Service"**

3. **Connect your GitHub repository**:
   - Choose your repository
   - Select the main branch

4. **Configure your web service**:
   - **Name**: `hatch-website` (or whatever you prefer)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn wsgi:app`
   - **Plan**: Free (or choose paid if you need more resources)

5. **Add Environment Variables**:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `WEBSITE_PASSWORD`: The password users will use to access your site
   - `SECRET_KEY`: Your secure secret key
   - `FLASK_ENV`: `production`
   - `FLASK_DEBUG`: `False`

6. **Click "Create Web Service"**

## Step 4: Wait for Deployment

- Render will automatically build and deploy your application
- This usually takes 5-10 minutes
- You'll see a green "Live" status when it's ready

## Step 5: Access Your Website

- Your website will be available at: `https://your-app-name.onrender.com`
- Share this URL with others!

## Important Notes

### Security
- **Never commit your .env file** to GitHub
- Use strong passwords and secret keys
- The website password will be required for anyone to access your site

### Limitations of Free Tier
- **Render Free Tier**:
  - Your app will "sleep" after 15 minutes of inactivity
  - First request after sleeping will take 30-60 seconds to wake up
  - 750 hours of runtime per month
  - 512 MB RAM, 0.1 CPU

### File Storage
- **Images and audio are stored locally** on Render's servers
- Files will persist between deployments
- Consider using cloud storage (AWS S3, Cloudinary) for production use

### Database
- **Current setup uses JSON files** for data storage
- For production, consider using a proper database (PostgreSQL, MongoDB)
- Render offers free PostgreSQL databases

## Troubleshooting

### Common Issues

1. **Build fails**: Check that all requirements are in `requirements.txt`
2. **App crashes**: Check the logs in Render dashboard
3. **Environment variables**: Ensure all required variables are set in Render
4. **File permissions**: The app should automatically create necessary directories

### Checking Logs

1. Go to your Render dashboard
2. Click on your web service
3. Go to the "Logs" tab
4. Look for any error messages

## Updating Your Website

1. Make changes to your code
2. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Update description"
   git push
   ```
3. Render will automatically redeploy your changes

## Alternative Hosting Options

If you prefer other platforms:

- **Heroku**: Similar to Render, but requires credit card for free tier
- **Railway**: Good free tier, easy deployment
- **DigitalOcean App Platform**: More control, but paid
- **AWS/GCP**: More complex but very scalable

## Need Help?

- Check Render's documentation: [docs.render.com](https://docs.render.com)
- Look at the logs in your Render dashboard
- Ensure all environment variables are set correctly
- Verify your OpenAI API key is valid and has credits

---

**Happy Deploying! 🐣**
