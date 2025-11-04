# Complete Auto-Deployment Setup for PythonAnywhere
# This script will set up everything needed for automatic deployment

Write-Host "🚀 PythonAnywhere Auto-Deployment Setup" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Green
Write-Host ""

# Step 1: Check if Git is installed
Write-Host "🔍 Step 1: Checking Git installation..." -ForegroundColor Yellow
$gitInstalled = $false
try {
    $gitVersion = & git --version 2>$null
    if ($gitVersion) {
        Write-Host "✅ Git is installed: $gitVersion" -ForegroundColor Green
        $gitInstalled = $true
    }
} catch {
    $gitInstalled = $false
}

if (-not $gitInstalled) {
    Write-Host "❌ Git is not installed!" -ForegroundColor Red
    Write-Host ""
    Write-Host "📥 Please install Git for Windows:" -ForegroundColor Yellow
    Write-Host "   1. Go to: https://git-scm.com/download/win" -ForegroundColor Cyan
    Write-Host "   2. Download and install Git" -ForegroundColor Cyan
    Write-Host "   3. Restart PowerShell" -ForegroundColor Cyan
    Write-Host "   4. Run this script again" -ForegroundColor Cyan
    Write-Host ""
    Read-Host "Press Enter after installing Git to continue"
    exit
}

Write-Host ""

# Step 2: Initialize repository
Write-Host "🔧 Step 2: Setting up Git repository..." -ForegroundColor Yellow
if (!(Test-Path ".git")) {
    git init
    Write-Host "✅ Git repository initialized" -ForegroundColor Green
} else {
    Write-Host "✅ Git repository already exists" -ForegroundColor Green
}

# Step 3: Create .gitignore
Write-Host ""
Write-Host "📝 Step 3: Creating .gitignore file..." -ForegroundColor Yellow
$gitignoreContent = @"
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Flask
instance/
.webassets-cache

# Environment variables
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Local database (if using SQLite in development)
# Uncomment if you want to exclude local database
# *.db

# Temporary files
*.tmp
*.temp

# Deployment files (we'll keep these in Git)
# deploy.ps1
# GIT_DEPLOYMENT_GUIDE.md
"@

$gitignoreContent | Out-File -FilePath ".gitignore" -Encoding UTF8
Write-Host "✅ .gitignore created" -ForegroundColor Green

# Step 4: Add files
Write-Host ""
Write-Host "📁 Step 4: Adding files to Git..." -ForegroundColor Yellow
git add .
Write-Host "✅ Files staged for commit" -ForegroundColor Green

# Step 5: Initial commit
Write-Host ""
Write-Host "💾 Step 5: Creating initial commit..." -ForegroundColor Yellow
git commit -m "Initial commit: Tidrapportering Flask app with mobile responsive design"
Write-Host "✅ Initial commit created" -ForegroundColor Green

# Step 6: Setup GitHub repository
Write-Host ""
Write-Host "🌐 Step 6: GitHub Repository Setup" -ForegroundColor Yellow
Write-Host "   1. Go to https://github.com" -ForegroundColor White
Write-Host "   2. Click 'New repository' (green button)" -ForegroundColor White
Write-Host "   3. Name it: tidrapportering" -ForegroundColor White
Write-Host "   4. Keep it Public (or Private if you prefer)" -ForegroundColor White
Write-Host "   5. DO NOT initialize with README, .gitignore, or license" -ForegroundColor Red
Write-Host "   6. Click 'Create repository'" -ForegroundColor White
Write-Host ""

$githubUsername = Read-Host "Enter your GitHub username"
if ([string]::IsNullOrEmpty($githubUsername)) {
    Write-Host "❌ GitHub username required!" -ForegroundColor Red
    exit
}

# Step 7: Add remote and push
Write-Host ""
Write-Host "🔗 Step 7: Connecting to GitHub..." -ForegroundColor Yellow
$remoteUrl = "https://github.com/$githubUsername/tidrapportering.git"
git remote add origin $remoteUrl

Write-Host "📤 Pushing to GitHub..." -ForegroundColor Yellow
Write-Host "   (You may be prompted for GitHub credentials)" -ForegroundColor Cyan
try {
    git branch -M main
    git push -u origin main
    Write-Host "✅ Successfully pushed to GitHub!" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to push to GitHub" -ForegroundColor Red
    Write-Host "   Make sure the repository exists and you have access" -ForegroundColor Yellow
    Write-Host "   Repository URL: $remoteUrl" -ForegroundColor Cyan
}

# Step 8: PythonAnywhere setup instructions
Write-Host ""
Write-Host "🐍 Step 8: PythonAnywhere Setup" -ForegroundColor Yellow
Write-Host "   Now run these commands in PythonAnywhere Bash console:" -ForegroundColor White
Write-Host ""
Write-Host "   # Navigate to your project directory" -ForegroundColor Gray
Write-Host "   cd /home/tidrproj/TIDR/A00000085" -ForegroundColor Cyan
Write-Host ""
Write-Host "   # Clone your repository" -ForegroundColor Gray
Write-Host "   git clone $remoteUrl ." -ForegroundColor Cyan
Write-Host ""
Write-Host "   # Make deployment script executable" -ForegroundColor Gray
Write-Host "   chmod +x deploy-from-git.sh" -ForegroundColor Cyan
Write-Host ""

Write-Host "✅ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "🎉 Your auto-deployment workflow is ready!" -ForegroundColor Green
Write-Host "   • Make changes to your code" -ForegroundColor White
Write-Host "   • Run deploy.ps1 to push changes" -ForegroundColor White
Write-Host "   • PythonAnywhere pulls changes automatically" -ForegroundColor White