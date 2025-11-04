#!/bin/bash
# PythonAnywhere Auto-Deploy Script
# This script pulls changes from GitHub and reloads the web app

echo "🚀 Auto-deploying from GitHub..."
echo "================================"

# Navigate to project directory
cd /home/tidrproj/TIDR/A00000085

# Pull latest changes
echo "📥 Pulling latest changes from GitHub..."
git pull origin main

if [ $? -eq 0 ]; then
    echo "✅ Successfully pulled changes"
    
    # Install any new requirements
    echo "📦 Installing/updating dependencies..."
    pip3.11 install --user -r requirements.txt
    
    # Reload the web app by touching WSGI file
    echo "🔄 Reloading web application..."
    touch /var/www/tidrproj_pythonanywhere_com_wsgi.py
    
    echo "✅ Deployment complete at $(date)"
    echo ""
    echo "🌐 Your app is live at: https://tidrproj.pythonanywhere.com"
else
    echo "❌ Failed to pull changes from GitHub"
    echo "Check your internet connection and repository access"
fi