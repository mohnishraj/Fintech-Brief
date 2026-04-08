#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# Fintech Intelligence Brief — One-Time GitHub Pages Setup
# Run this ONCE from your Mac terminal inside the project folder.
# After this, every daily brief auto-deploys via git push in the scheduled task.
# ═══════════════════════════════════════════════════════════════════════════════
set -e

REPO_URL="${1:-}"

if [ -z "$REPO_URL" ]; then
  echo ""
  echo "Usage: bash setup-github-pages.sh <your-github-repo-url>"
  echo ""
  echo "Example:"
  echo "  bash setup-github-pages.sh https://github.com/mohnish/fintech-brief.git"
  echo ""
  echo "Steps to get your repo URL:"
  echo "  1. Go to github.com → New repository"
  echo "  2. Name it: fintech-brief  (or anything you like)"
  echo "  3. Set visibility: Private (recommended) or Public"
  echo "  4. Do NOT initialise with README"
  echo "  5. Copy the HTTPS clone URL and pass it here"
  echo ""
  exit 1
fi

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo ""
echo "── Initialising git repo …"
git init
git branch -m main

echo "── Staging all files …"
git add -A

echo "── Creating initial commit …"
git commit -m "feat: Fintech Intelligence Brief — initial archive (Editions 001–003)"

echo "── Adding remote origin …"
git remote add origin "$REPO_URL"

echo "── Pushing to GitHub …"
git push -u origin main

echo ""
echo "═══════════════════════════════════════════════════════"
echo "✅ Pushed! Now enable GitHub Pages:"
echo ""
echo "  1. Open: ${REPO_URL/\.git/}/settings/pages"
echo "  2. Source  →  Deploy from a branch"
echo "  3. Branch  →  main   /  (root)"
echo "  4. Save"
echo ""
echo "Your archive dashboard will be live at:"
PAGES_URL=$(echo "$REPO_URL" | sed 's/https:\/\/github.com\//https:\/\//' | sed 's/\.git$//' | sed 's/\//\.github\.io\//')
echo "  $PAGES_URL/brief-archive.html"
echo ""
echo "Each new brief will be at:"
echo "  $PAGES_URL/briefs/brief-YYYY-MM-DD.html"
echo "═══════════════════════════════════════════════════════"
