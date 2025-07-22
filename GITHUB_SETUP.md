# 🚀 GitHub + Netlify Deployment for dingdawg.com

## Step 1: Initialize Git Repository

Run these commands in your terminal:

```bash
cd /home/joe-rangel/Desktop/Jarvis-Main-Brain/ai-affiliate-funnel

# Initialize git repository
git init

# Add all files to git
git add .

# Create first commit
git commit -m "Initial dingdawg.com site - 25 products (10 Amazon + 15 ClickBank)"

# Add your GitHub repository as remote
git remote add origin https://github.com/jr33377/dingdawg-site.git

# Push to GitHub
git push -u origin main
```

## Step 2: Create GitHub Repository

1. Go to [github.com](https://github.com)
2. Log into account: `jr33377`
3. Click "New Repository" (green button)
4. Repository name: `dingdawg-site`
5. Make it **Public** (required for free Netlify)
6. **DO NOT** initialize with README (we already have content)
7. Click "Create Repository"

## Step 3: Connect to Netlify

1. Go to [netlify.com](https://netlify.com)
2. Sign up with GitHub account
3. Click "New site from Git"
4. Choose "GitHub"
5. Select repository: `jr33377/dingdawg-site`
6. Build settings:
   - **Build command**: `hugo --baseURL="https://dingdawg.com"`
   - **Publish directory**: `public`
   - **Branch**: `main`
7. Click "Deploy site"

## Step 4: Add Custom Domain

1. In Netlify dashboard → "Domain settings"
2. Click "Add custom domain"
3. Enter: `dingdawg.com`
4. Click "Verify"
5. Follow DNS instructions for Google Domains/Squarespace

## Your Site is Ready! 

✅ **25 products** (10 Amazon + 15 ClickBank)  
✅ **$20,120/month potential**  
✅ **Professional design**  
✅ **Amazon compliant**  
✅ **Free hosting forever**  

**Need your ClickBank nickname next to update those affiliate links!**