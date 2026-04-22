# NeuroShield GitHub Push Automation Script
# Created by Antigravity AI

Write-Host "--- Starting NeuroShield GitHub Push Automation ---" -ForegroundColor Cyan

# 1. Verify Git Initialization
if (!(Test-Path .git)) {
    Write-Host "Initializing Git repository..." -ForegroundColor Yellow
    git init
}

# 2. Add and Commit (if anything is new)
Write-Host "Staging files..." -ForegroundColor Yellow
git add .
$status = git status --porcelain
if ($status) {
    Write-Host "Committing changes..." -ForegroundColor Yellow
    git commit -m "Auto-commit: Preparing for GitHub push"
} else {
    Write-Host "No new changes to commit." -ForegroundColor Green
}

# 3. Ensure branch is main
Write-Host "Switching to main branch..." -ForegroundColor Yellow
git branch -M main

# 4. Configure Remote
$remote = "https://github.com/subhechhamaiti716-byte/NeuroShield-AI-Fraud-Detection-App.git"
$currentRemote = git remote get-url origin 2>$null
if ($currentRemote -ne $remote) {
    Write-Host "Setting remote origin..." -ForegroundColor Yellow
    git remote remove origin 2>$null
    git remote add origin $remote
}

# 5. Final Push
Write-Host ""
Write-Host "--- IMPORTANT ---" -ForegroundColor Red
Write-Host "Please ensure you have created the repository on GitHub:" -ForegroundColor White
Write-Host "https://github.com/subhechhamaiti716-byte/NeuroShield-AI-Fraud-Detection-App" -ForegroundColor Green
Write-Host "-----------------" -ForegroundColor Red
Write-Host ""
Write-Host "Attempting to push to GitHub..." -ForegroundColor Cyan

# Try pushing
git push -u origin main

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "PUSH FAILED!" -ForegroundColor Red
    Write-Host "Possible causes:" -ForegroundColor Yellow
    Write-Host "1. Repository does not exist on GitHub yet."
    Write-Host "2. Authentication failure (check your Personal Access Token)."
    Write-Host "3. Remote contains work that you do not have locally (try 'git pull --rebase origin main')."
} else {
    Write-Host ""
    Write-Host "PUSH SUCCESSFUL!" -ForegroundColor Green
}

Write-Host ""
Pause
