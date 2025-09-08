#!/bin/bash

# Auto Push Script for CRM/ERP System
# This script automatically commits and pushes changes to GitHub

set -e

echo "🚀 Starting Auto Push Process..."

# Get current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Error: Not in a git repository"
    exit 1
fi

# Get current branch
CURRENT_BRANCH=$(git branch --show-current)
echo "📍 Current branch: $CURRENT_BRANCH"

# Check for changes
if git diff --quiet && git diff --cached --quiet; then
    echo "ℹ️  No changes to commit"
    exit 0
fi

# Add all changes
echo "📝 Adding all changes..."
git add .

# Get commit message from user or use default
if [ -z "$1" ]; then
    COMMIT_MSG="Auto commit: $(date '+%Y-%m-%d %H:%M:%S')"
else
    COMMIT_MSG="$1"
fi

# Commit changes
echo "💾 Committing changes..."
git commit -m "$COMMIT_MSG"

# Push to current branch
echo "⬆️  Pushing to $CURRENT_BRANCH..."
git push origin "$CURRENT_BRANCH"

# Also push to main if not already on main
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "🔄 Also updating main branch..."
    git checkout main
    git reset --hard "$CURRENT_BRANCH"
    git push origin main --force
    git checkout "$CURRENT_BRANCH"
fi

echo "✅ Auto push completed successfully!"
echo "🌐 Check your repository at: https://github.com/hamidrezasoltanian/hamidreza-soltanian"