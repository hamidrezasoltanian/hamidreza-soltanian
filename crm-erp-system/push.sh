#!/bin/bash

# Simple Push Script
# Usage: ./push.sh "commit message"

set -e

echo "🚀 Quick Push to GitHub..."

# Add all changes
git add .

# Commit with message
if [ -z "$1" ]; then
    git commit -m "Update: $(date '+%Y-%m-%d %H:%M:%S')"
else
    git commit -m "$1"
fi

# Push to current branch
git push origin $(git branch --show-current)

# Also update main branch
echo "🔄 Updating main branch..."
git checkout main
git reset --hard $(git branch --show-current)
git push origin main --force

echo "✅ Pushed successfully to GitHub!"