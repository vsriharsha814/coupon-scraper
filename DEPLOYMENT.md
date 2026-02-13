# Deployment Guide

## Option 1: Deploy to Railway (Recommended - Simplest)

### Setup:
1. Push your code to GitHub (make sure you have a GitHub account)
2. Go to [railway.app](https://railway.app) and sign up
3. Click "New Project" and select "Deploy from GitHub repo"
4. Select your `coupon-scraper` repository
5. Railway will automatically detect the `Procfile` and deploy your app

### Important Notes:
- **Selenium/Chrome Issue**: Your script uses Selenium with Chrome/Brave. Railway's environment may not have Chrome installed by default.
- **Solution**: You'll need to add a buildpack or use a custom Dockerfile that includes Chrome.

---

## Option 2: Deploy to Render

### Setup:
1. Go to [render.com](https://render.com) and sign up
2. Click "New +" and select "Web Service"
3. Connect your GitHub repository
4. Set the build command: `pip install -r requirements.txt`
5. Set the start command: `cd webapp && python app.py`
6. Deploy

---

## Option 3: Deploy to Vercel (Alternative)

### Setup:
1. Go to [vercel.com](https://vercel.com) and sign up with GitHub
2. Click "Add New" and select "Project"
3. Import your GitHub repository
4. Vercel will auto-detect it's a Python Flask app
5. Deploy

---

## Important: Fix the Selenium/Chrome Issue

Since your script requires Chrome/Brave browser, you need to handle this for cloud deployment:

### Quick Fix for Local Testing:
```bash
cd /Users/harsha/Documents/Projects/coupon-scraper
pip install -r requirements.txt
python webapp/app.py
```

Then visit: `http://localhost:5000`

### For Production (Cloud):
The script will fail if Chrome isn't available. You have two options:

**Option A**: Modify your script to handle missing Chrome gracefully
**Option B**: Use a service like BrowserStack or ScrapingBee API instead of local Selenium

---

## Steps to Deploy Right Now:

1. **Commit and push to GitHub**:
   ```bash
   cd /Users/harsha/Documents/Projects/coupon-scraper
   git add .
   git commit -m "Add Flask web app for coupon scraper"
   git push
   ```

2. **Choose a platform** (Railway recommended):
   - Go to railway.app
   - Sign up with GitHub
   - Create new project from your GitHub repo
   - Railway will handle the rest

3. **Handle Chrome dependency**:
   - You may see deployment errors related to Chrome
   - If so, we'll need to create a Dockerfile with Chrome pre-installed
   - Let me know if you get deployment errors!

---

## Testing Locally First:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the Flask app
cd /Users/harsha/Documents/Projects/coupon-scraper
python webapp/app.py

# Visit http://localhost:5000 in your browser
```

Click "Run Script" to test it works locally before deploying to the cloud!
