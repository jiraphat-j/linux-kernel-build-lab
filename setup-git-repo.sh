#!/usr/bin/env bash
# Bash Script: Initialize Git Repository and Branches for CPE 333 Mini-Project 1
set -e

echo "=== Initializing CPE 333 Mini-Project 1 Git Repository ==="

# 1. Initialize Git repository
git init

# 2. Stage all initial files
git add .

# 3. Create initial commit
git commit -m "feat: initialize repository structure, templates, and guides for CPE333 Mini-Project 1"

# 4. Ensure branch is 'main'
git branch -M main

# 5. Create the required feature branches
for b in build report troubleshooting comparison; do
    git branch "$b"
    echo " -> Created branch: $b"
done

# 6. Switch back to main
git checkout main

echo ""
echo "=== Repository initialized successfully! ==="
echo "Next Steps for the Lead:"
echo "1. Create a new repository on GitHub (e.g. 'os-mini-project-1-kernel-build')."
echo "2. Link your local repo to GitHub with:"
echo "   git remote add origin https://github.com/<your-username>/<repo-name>.git"
echo "3. Push all branches to GitHub:"
echo "   git push -u origin main"
echo "   git push --all origin"
echo "4. Go to GitHub Settings -> Collaborators -> Invite your team members."
