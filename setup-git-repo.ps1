# PowerShell Script: Initialize Git Repository and Branches for CPE 333 Mini-Project 1
Write-Host "=== Initializing CPE 333 Mini-Project 1 Git Repository ===" -ForegroundColor Cyan

# 1. Initialize Git repository
git init
if ($LASTEXITCODE -ne 0) {
    Write-Error "Git init failed. Ensure Git is installed and in your PATH."
    exit 1
}

# 2. Stage all initial files
git add .

# 3. Create initial commit
git commit -m "feat: initialize repository structure, templates, and guides for CPE333 Mini-Project 1"

# 4. Ensure branch is 'main'
git branch -M main

# 5. Create the required feature branches
$branches = @("build", "report", "troubleshooting", "comparison")
foreach ($b in $branches) {
    git branch $b
    Write-Host " -> Created branch: $b" -ForegroundColor Green
}

# 6. Switch back to main
git checkout main

Write-Host "`n=== Repository initialized successfully! ===" -ForegroundColor Green
Write-Host "Next Steps for the Lead:" -ForegroundColor Yellow
Write-Host "1. Create a new repository on GitHub (e.g. 'os-mini-project-1-kernel-build')."
Write-Host "2. Link your local repo to GitHub with:"
Write-Host "   git remote add origin https://github.com/<your-username>/<repo-name>.git"
Write-Host "3. Push all branches to GitHub:"
Write-Host "   git push -u origin main"
Write-Host "   git push --all origin"
Write-Host "4. Go to GitHub Settings -> Collaborators -> Invite your team members."
