# Complete Setup Guide

This guide walks you through every step to get your recipe site running.

## Part 1: Local Setup (First Time)

### Step 1: No Export Needed! ✨

**Good news:** The script now reads directly from Safari's Reading List - no manual export required!

Just make sure you have recipes saved in your Safari Reading List:
- In Safari, click the sidebar icon (or View → Show Reading List)
- You should see your saved recipes there

### Step 2: Set Up Project on Your Computer

Open Terminal (press Cmd+Space, type "Terminal", press Enter) and run:

```bash
# Navigate to where you want the project (e.g., Documents)
cd ~/Documents

# Download the project (if you have it as a zip, unzip it first)
# Or if creating from scratch, create the directory
mkdir recipe-site
cd recipe-site

# Copy all the files we created into this folder
```

### Step 3: Install Python Dependencies

```bash
# Create a virtual environment (keeps packages isolated)
python3 -m venv venv

# Activate it
source venv/bin/activate

# Your prompt should now show (venv) at the start
# Install required packages
pip install -r requirements.txt
```

**What this does:** Creates an isolated Python environment and installs the recipe scraping libraries.

### Step 4: Scrape Your Recipes

```bash
# Run the scraper
python scripts/scrape_recipes.py
```

**What happens:** 
- Reads your Safari Reading List directly from `~/Library/Safari/Bookmarks.plist`
- Visits each recipe URL
- Extracts structured recipe data
- Saves everything to `data/recipes.json`

This will take a few minutes depending on how many recipes you have.

**Note:** This must run on your Mac - it accesses Safari's database file.

### Step 5: Generate the Website

```bash
# Build the static site
python scripts/generate_site.py
```

**What happens:** Creates a mobile-friendly HTML website in the `site/` folder.

### Step 6: Test Locally

```bash
# Start a local web server
python -m http.server 8000 --directory site
```

Open your browser and go to: **http://localhost:8000**

You should see your recipe site! Press Ctrl+C in Terminal to stop the server.

---

## Part 2: Deploy to GitHub Pages

### Step 1: Create a GitHub Account

If you don't have one: Go to https://github.com/signup

### Step 2: Create a New Repository

1. Go to https://github.com/new
2. Repository name: `recipe-site` (or whatever you prefer)
3. Make it **Public** (required for free GitHub Pages)
4. **Do NOT** initialize with README
5. Click "Create repository"

### Step 3: Push Your Code to GitHub

Back in Terminal (in your recipe-site folder):

```bash
# Initialize git repository
git init

# Add all files
git add .

# Make first commit
git commit -m "Initial commit: Recipe site setup"

# Connect to GitHub (replace YOUR-USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR-USERNAME/recipe-site.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**Important:** GitHub will ask for your username and password. For password, you need to create a Personal Access Token:
1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Give it a name like "recipe-site"
4. Check the "repo" box
5. Click "Generate token"
6. Copy the token and use it as your password

### Step 4: Enable GitHub Pages

1. Go to your repository on GitHub
2. Click **Settings** (top right)
3. Click **Pages** (left sidebar)
4. Under "Source", select **GitHub Actions**
5. Click "Save"

### Step 5: Wait for Deployment

1. Click the **Actions** tab in your repository
2. You should see a workflow running
3. Wait for it to complete (green checkmark)
4. Your site will be live at: `https://YOUR-USERNAME.github.io/recipe-site/`

---

## Part 3: Updating Your Recipe Site

### When You Add New Recipes to Safari Reading List

**Option A: Run Locally Then Push**

Just add recipes to your Safari Reading List as normal, then:

```bash
cd ~/Documents/recipe-site

# Activate virtual environment
source venv/bin/activate

# Re-scrape recipes (picks up new ones automatically)
python scripts/scrape_recipes.py

# Rebuild site
python scripts/generate_site.py

# Commit and push to GitHub
git add data/recipes.json site/
git commit -m "Updated recipes"
git push

# Site will automatically deploy
```

**Option B: Automatic (Scheduled)**

Set up a cron job on your Mac to run the scraper daily:

```bash
# Edit crontab
crontab -e

# Add this line (runs daily at 3 AM):
0 3 * * * cd ~/Documents/recipe-site && source venv/bin/activate && python scripts/scrape_recipes.py && python scripts/generate_site.py && git add -A && git commit -m "Auto-update recipes" && git push
```

**Note:** For fully automatic updates, your Mac needs to be:
- Turned on at the scheduled time
- Connected to the internet
- Not in sleep mode (or enable "prevent sleep" in cron job)

---

## Troubleshooting

### Problem: "Recipe scraper failed for some URLs"

**Solution:** Some websites don't have proper recipe markup. The scraper will skip them but continue with others. Check `data/recipes.json` to see which failed.

### Problem: "Module not found" errors

**Solution:** Make sure you activated the virtual environment:
```bash
source venv/bin/activate
```

### Problem: GitHub Pages not updating

**Solution:**
1. Check the Actions tab for errors
2. Ensure `data/Bookmarks.html` exists in your repository
3. Re-run the workflow: Actions → Click workflow → "Re-run jobs"

### Problem: Images not loading

**Solution:** Some recipe sites block image hotlinking. The site has fallback placeholder images.

### Problem: Recipe looks wrong

**Solution:** You can manually edit `data/recipes.json` to fix any issues, then run `python scripts/generate_site.py` again.

---

## Customization Tips

### Change Colors

Edit `scripts/generate_site.py` and modify the CSS variables in the `:root` section:

```css
:root {
    --primary: #2563eb;        /* Main color */
    --primary-dark: #1e40af;   /* Hover color */
    --bg: #f8fafc;             /* Background */
}
```

### Add More Features

The site is built with vanilla HTML/CSS/JavaScript, so you can easily add:
- Recipe ratings
- Favorite/bookmark functionality
- Print button
- Shopping list generator
- Recipe notes

Just edit the `generate_html()` function in `generate_site.py`.

---

## File Structure Explained

```
recipe-site/
├── scripts/
│   ├── scrape_recipes.py      # Extracts recipes from bookmarks
│   └── generate_site.py       # Builds the website
│
├── site/                      # Generated website (deploy this)
│   └── index.html            # Your recipe site
│
├── data/
│   ├── Bookmarks.html        # Your Safari bookmarks export
│   └── recipes.json          # Structured recipe data
│
├── .github/workflows/
│   └── deploy.yml            # Automation configuration
│
├── requirements.txt          # Python dependencies
└── README.md                 # Documentation
```

---

## Next Steps

1. ✅ Follow Part 1 to set up locally
2. ✅ Test that everything works
3. ✅ Follow Part 2 to deploy to GitHub Pages
4. ✅ Share your recipe site URL with friends!

**Your site will be at:** `https://YOUR-USERNAME.github.io/recipe-site/`
