# Simple Auto-Deployment Setup for PythonAnywhere
Write-Host "🚀 PythonAnywhere Auto-Deployment Setup" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Green
Write-Host ""

# Check if Git is installed
Write-Host "🔍 Checking Git..." -ForegroundColor Yellow
$gitInstalled = Get-Command git -ErrorAction SilentlyContinue
if (-not $gitInstalled) {
    Write-Host "❌ Git not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "📥 Please install Git:" -ForegroundColor Yellow
    Write-Host "   1. Go to: https://git-scm.com/download/win" -ForegroundColor Cyan
    Write-Host "   2. Download and install Git for Windows" -ForegroundColor Cyan
    Write-Host "   3. Restart PowerShell and run this script again" -ForegroundColor Cyan
    exit
}

Write-Host "✅ Git found!" -ForegroundColor Green

# Initialize repository if needed
if (!(Test-Path ".git")) {
    Write-Host ""
    Write-Host "🔧 Initializing Git repository..." -ForegroundColor Yellow
    git init
    Write-Host "✅ Git repository initialized" -ForegroundColor Green
} else {
    Write-Host "✅ Git repository already exists" -ForegroundColor Green
}

# Create .gitignore
Write-Host ""
Write-Host "📝 Creating .gitignore..." -ForegroundColor Yellow
@"
__pycache__/
*.pyc
.env
venv/
.vscode/
*.log
Thumbs.db
.DS_Store
"@ | Out-File -FilePath ".gitignore" -Encoding UTF8

# Add and commit files
Write-Host ""
Write-Host "📁 Adding files to Git..." -ForegroundColor Yellow
git add .
git commit -m "Initial commit: Tidrapportering Flask app"
Write-Host "✅ Files committed" -ForegroundColor Green

# Get GitHub username
Write-Host ""
Write-Host "🌐 GitHub Setup" -ForegroundColor Yellow
$githubUsername = Read-Host "Enter your GitHub username"

if ($githubUsername) {
    # Add remote
    $repoUrl = "https://github.com/$githubUsername/tidrapportering.git"
    git remote add origin $repoUrl
    
    Write-Host ""
    Write-Host "📋 Next Steps:" -ForegroundColor Yellow
    Write-Host "1. Create a repository on GitHub named 'tidrapportering'" -ForegroundColor White
    Write-Host "2. Then run: git push -u origin main" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "🔄 After that, use .\deploy.ps1 to push changes" -ForegroundColor Green
} else {
    Write-Host "⚠️  Skipping GitHub setup" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "✅ Setup complete!" -ForegroundColor Green