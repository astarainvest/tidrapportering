# Quick Deploy Script for PythonAnywhere
# Run this after making changes to automatically commit and push

Write-Host "🚀 Deploying changes to GitHub..." -ForegroundColor Green

# Check if git is initialized
if (!(Test-Path ".git")) {
    Write-Host "❌ Git not initialized. Run setup first!" -ForegroundColor Red
    Write-Host "   Run: .\setup-auto-deployment.ps1" -ForegroundColor Yellow
    exit
}

# Check for changes
$status = git status --porcelain
if ([string]::IsNullOrEmpty($status)) {
    Write-Host "ℹ️  No changes to deploy" -ForegroundColor Cyan
    exit
}

Write-Host "📁 Files changed:" -ForegroundColor Yellow
git status --short

# Add all changes
git add .

# Get commit message
$message = Read-Host "Commit message (press Enter for default)"
if ([string]::IsNullOrEmpty($message)) { 
    $message = "Update app files - $(Get-Date -Format 'yyyy-MM-dd HH:mm')" 
}

# Commit and push
try {
    git commit -m $message
    git push origin main
    Write-Host "✅ Successfully pushed to GitHub!" -ForegroundColor Green
    Write-Host ""
    Write-Host "� Auto-deploying on PythonAnywhere..." -ForegroundColor Yellow
    Write-Host "   Run this in PythonAnywhere Bash console:" -ForegroundColor White
    Write-Host "   ./deploy-from-git.sh" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "🌐 Your app will be live at: https://tidrproj.pythonanywhere.com" -ForegroundColor Green
}
catch {
    Write-Host "❌ Error during deployment: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "   Make sure you have access to the GitHub repository" -ForegroundColor Yellow
}