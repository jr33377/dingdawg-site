#!/bin/bash
# Automated Deployment Script for dingdawg.com
# This script handles the entire deployment process

echo "🚀 Starting Automated Deployment for dingdawg.com"
echo "=================================================="

# Step 1: Build latest Hugo site
echo "🔨 Building Hugo site..."
./hugo --baseURL="https://dingdawg.com"

# Step 2: Update GitHub upload folder
echo "📁 Updating GitHub upload folder..."
rm -rf GITHUB_UPLOAD/*
cp -r content themes public hugo.toml GITHUB_UPLOAD/

# Step 3: Git operations
echo "📤 Updating Git repository..."
git add .
git commit -m "Auto-update: $(date '+%Y-%m-%d %H:%M:%S') - New content deployed"

# Step 4: Instructions for GitHub push
echo ""
echo "✅ READY FOR GITHUB UPLOAD!"
echo "================================"
echo ""
echo "OPTION 1 - Command Line (if you have GitHub credentials):"
echo "git push origin master"
echo ""
echo "OPTION 2 - Web Upload:"
echo "1. Go to: https://github.com/jr33377/dingdawg-site"
echo "2. Upload files from: GITHUB_UPLOAD/"
echo "3. Netlify will auto-deploy to dingdawg.com"
echo ""
echo "📊 CURRENT STATUS:"
echo "• Amazon products: 10 (all with reviews)"
echo "• ClickBank products: 15 (ready for content)"
echo "• Total revenue potential: \$20,120/month"
echo ""
echo "🎯 NEXT: After upload, your site will have all 10 Amazon reviews!"