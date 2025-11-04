# PythonAnywhere Auto-Upload Script
# This script monitors your local files and uploads changes to PythonAnywhere

param(
    [string]$Username = "tidrproj",
    [string]$LocalPath = "C:\Users\Ali Eghtedari\My Drive\NAMIN\A00000085",
    [string]$RemotePath = "/home/tidrproj/TIDR/A00000085"
)

Write-Host "🚀 PythonAnywhere Auto-Upload Script" -ForegroundColor Green
Write-Host "Monitoring: $LocalPath" -ForegroundColor Yellow
Write-Host "Target: $Username at $RemotePath" -ForegroundColor Yellow
Write-Host ""

# Function to upload a single file
function Upload-File {
    param($FilePath, $RelativePath)
    
    Write-Host "📤 Uploading: $RelativePath" -ForegroundColor Cyan
    
    # You can use scp, rsync, or PythonAnywhere's API here
    # For now, this shows which files would be uploaded
    Write-Host "   ✅ $FilePath ready for upload" -ForegroundColor Green
}

# Get all files (excluding unnecessary ones)
$excludePatterns = @(
    "*.pyc", "__pycache__", ".git", "node_modules", 
    "*.log", ".env", "venv", ".vscode",
    "RESTORATION_COMPLETE.md", "PYTHONANYWHERE_DEPLOYMENT.md"
)

Write-Host "🔍 Scanning for files to upload..." -ForegroundColor Yellow

# Files to upload
$filesToUpload = @(
    "app.py",
    "wsgi.py", 
    "requirements.txt",
    "static\css\style.css",
    "static\js\main.js",
    "templates\*.html",
    "templates\admin\*.html"
)

foreach ($pattern in $filesToUpload) {
    $files = Get-ChildItem -Path $LocalPath -Filter $pattern -Recurse -File
    foreach ($file in $files) {
        $relativePath = $file.FullName.Substring($LocalPath.Length + 1)
        Upload-File -FilePath $file.FullName -RelativePath $relativePath
    }
}

Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Green
Write-Host "1. Upload these files manually to PythonAnywhere Files section" -ForegroundColor White
Write-Host "2. Or set up Git repository for automatic sync" -ForegroundColor White
Write-Host "3. Or configure SCP/SFTP for direct upload" -ForegroundColor White

# Watch for changes (optional)
Write-Host ""
$watch = Read-Host "Do you want to watch for file changes? (y/n)"
if ($watch -eq "y") {
    Write-Host "👀 Watching for changes... (Press Ctrl+C to stop)" -ForegroundColor Yellow
    
    $watcher = New-Object System.IO.FileSystemWatcher
    $watcher.Path = $LocalPath
    $watcher.Filter = "*.*"
    $watcher.IncludeSubdirectories = $true
    $watcher.EnableRaisingEvents = $true
    
    $action = {
        $path = $Event.SourceEventArgs.FullPath
        $name = $Event.SourceEventArgs.Name
        $changeType = $Event.SourceEventArgs.ChangeType
        
        # Only monitor relevant files
        if ($name -match "\.(py|html|css|js|txt)$") {
            Write-Host "🔔 File ${changeType}: $name" -ForegroundColor Magenta
            # Here you would trigger the upload
        }
    }
    
    Register-ObjectEvent -InputObject $watcher -EventName "Changed" -Action $action
    Register-ObjectEvent -InputObject $watcher -EventName "Created" -Action $action
    Register-ObjectEvent -InputObject $watcher -EventName "Deleted" -Action $action
    
    try {
        while ($true) {
            Start-Sleep 1
        }
    } finally {
        $watcher.EnableRaisingEvents = $false
        $watcher.Dispose()
    }
}