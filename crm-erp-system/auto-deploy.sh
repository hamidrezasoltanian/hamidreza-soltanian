#!/bin/bash

# Auto-Deploy Script
# This script automatically pushes changes to GitHub and deploys the system

set -euo pipefail

echo "🤖 Auto-Deploy Script for CRM/ERP System"
echo "========================================"
echo

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }
print_step() { echo -e "${PURPLE}[STEP]${NC} $1"; }

# Configuration
REPO_URL="https://github.com/hamidrezasoltanian/hamidreza-soltanian.git"
BRANCH_NAME="main"
COMMIT_MESSAGE="${1:-Auto-deploy $(date '+%Y-%m-%d %H:%M:%S')}"

# Function to check if we're in a git repository
check_git_repo() {
  if [ ! -d ".git" ]; then
    print_error "Not in a git repository. Please run this script from the project root."
    exit 1
  fi
}

# Function to check for uncommitted changes
check_changes() {
  if [ -n "$(git status --porcelain)" ]; then
    print_status "Found uncommitted changes. Adding and committing..."
    git add .
    git commit -m "$COMMIT_MESSAGE"
    print_success "Changes committed locally"
  else
    print_status "No uncommitted changes found"
  fi
}

# Function to push to GitHub
push_to_github() {
  print_step "📤 Pushing changes to GitHub..."
  
  # Check if remote exists
  if ! git remote get-url origin >/dev/null 2>&1; then
    print_status "Adding remote origin..."
    git remote add origin "$REPO_URL"
  fi
  
  # Push to GitHub
  print_status "Pushing to origin/$BRANCH_NAME..."
  git push origin "$BRANCH_NAME" || {
    print_warning "Push failed. Trying to set upstream..."
    git push --set-upstream origin "$BRANCH_NAME"
  }
  
  print_success "Changes pushed to GitHub successfully"
}

# Function to deploy the system
deploy_system() {
  print_step "🚀 Deploying system..."
  
  # Make deploy script executable
  chmod +x deploy.sh
  
  # Run deployment
  ./deploy.sh
  
  print_success "System deployed successfully"
}

# Function to show final status
show_final_status() {
  echo
  echo "🎉 Auto-Deploy Completed Successfully!"
  echo "====================================="
  echo
  echo "📊 GitHub Repository: $REPO_URL"
  echo "🌿 Branch: $BRANCH_NAME"
  echo "📝 Last Commit: $COMMIT_MESSAGE"
  echo
  echo "🌐 System URLs:"
  echo "   Frontend: http://localhost:3000"
  echo "   Backend: http://localhost:8000"
  echo "   Admin: http://localhost:8000/admin"
  echo
  echo "🔑 Login: admin / admin123"
  echo
  echo "🛠️ Management Commands:"
  echo "   Stop: ./stop.sh"
  echo "   Restart: ./restart.sh"
  echo "   Test: ./test.sh"
  echo "   Update: ./update.sh"
  echo
}

# Main execution
main() {
  print_step "Starting Auto-Deploy Process..."
  
  check_git_repo
  check_changes
  push_to_github
  deploy_system
  show_final_status
  
  print_success "🎉 Auto-Deploy completed successfully!"
}

# Run main function
main "$@"