#!/bin/bash

# Simple Push and Deploy Script
# Usage: ./push-and-deploy.sh [commit_message]

set -euo pipefail

echo "🚀 Push and Deploy Script"
echo "========================="
echo

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }

# Get commit message
COMMIT_MSG="${1:-Update $(date '+%Y-%m-%d %H:%M:%S')}"

print_status "Commit message: $COMMIT_MSG"

# Check git status
print_status "Checking git status..."
if [ -n "$(git status --porcelain)" ]; then
  print_status "Found changes. Adding and committing..."
  git add .
  git commit -m "$COMMIT_MSG"
  print_success "Changes committed"
else
  print_warning "No changes to commit"
fi

# Push to GitHub
print_status "Pushing to GitHub..."
git push origin main
print_success "Pushed to GitHub"

# Deploy locally
print_status "Deploying locally..."
chmod +x deploy.sh
./deploy.sh

print_success "🎉 Push and Deploy completed!"
echo
echo "🌐 System is running at:"
echo "   Frontend: http://localhost:3000"
echo "   Backend: http://localhost:8000"
echo "   Admin: http://localhost:8000/admin"
echo
echo "🔑 Login: admin / admin123"