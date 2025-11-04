# Git-Based Auto Deployment to PythonAnywhere
# This is the BEST method for automatic sync

## Setup Instructions:

### Step 1: Create GitHub Repository
1. Go to GitHub.com and create a new repository called "tidrapportering"
2. Don't initialize with README (we'll push existing code)

### Step 2: Initialize Local Git Repository
# Run these commands in PowerShell in your project folder:

cd "C:\Users\Ali Eghtedari\My Drive\NAMIN\A00000085"

# Initialize git
git init

# Add all files
git add .

# Make first commit
git commit -m "Initial commit - Tidrapportering Flask app"

# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/tidrapportering.git

# Push to GitHub
git push -u origin main

### Step 3: Setup PythonAnywhere Git Integration
1. In PythonAnywhere, go to Bash console
2. Navigate to your project directory:
   cd /home/tidrproj/TIDR/A00000085
3. Clone your repository:
   git clone https://github.com/YOUR_USERNAME/tidrapportering.git .
4. Set up automatic pull script

### Step 4: Create Auto-Deploy Script (on PythonAnywhere)
# Create this file in PythonAnywhere: /home/tidrproj/deploy.sh

#!/bin/bash
cd /home/tidrproj/TIDR/A00000085
git pull origin main
touch /var/www/tidrproj_pythonanywhere_com_wsgi.py
echo "Deployment complete at $(date)"

### Step 5: Auto-Deploy from Local Changes
# Use this PowerShell script whenever you make changes:

git add .
git commit -m "Updated app files"
git push origin main

# Then run this command to deploy on PythonAnywhere:
# (You can automate this with webhooks later)

## Benefits:
- ✅ Version control for your code
- ✅ Backup of all changes
- ✅ Easy rollback if something breaks
- ✅ Professional development workflow
- ✅ Can be automated with GitHub Actions later

## Quick Deploy Commands (save as deploy.ps1):
Write-Host "🚀 Deploying to PythonAnywhere..." -ForegroundColor Green
git add .
$message = Read-Host "Commit message (or press Enter for default)"
if ([string]::IsNullOrEmpty($message)) { $message = "Update app files" }
git commit -m $message
git push origin main
Write-Host "✅ Pushed to GitHub! Now pull on PythonAnywhere" -ForegroundColor Green