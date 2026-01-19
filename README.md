# Recipe Site

A mobile-first web app that automatically syncs with your Safari Reading List to display your saved recipes.

## Features
- 📱 Mobile-optimized interface
- 🔍 Search and filter recipes
- 📖 Clean, readable recipe cards
- 🔄 Automatic updates from Safari Reading List
- 📥 Offline-capable PWA
- 🍎 Reads directly from Safari (no manual export needed!)

## Setup Instructions

### 1. Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
```

### 2. Run the Scraper

```bash
python scripts/scrape_recipes.py
```

This will:
- Read your Safari Reading List directly from `~/Library/Safari/Bookmarks.plist`
- Extract recipes from each URL
- Save structured data to `data/recipes.json`

**Note:** This must run on a Mac with Safari installed.

### 3. Generate the Site

```bash
python scripts/generate_site.py
```

This creates the static HTML site in the `site/` folder.

### 4. Test Locally

```bash
# Simple local server
python -m http.server 8000 --directory site

# Open http://localhost:8000 in your browser
```

### 5. Deploy to GitHub Pages

1. Create a new GitHub repository
2. Push this code to the repository
3. Go to Settings → Pages
4. Set source to "GitHub Actions"
5. The site will automatically build and deploy!

## Automatic Updates

The GitHub Actions workflow runs daily at 2 AM UTC and checks for new recipes in your Reading List. 

**For GitHub Actions to access your Reading List:**
- The workflow needs to run on your Mac (using a self-hosted runner), OR
- You can manually trigger builds by pushing a commit after adding new recipes

## Folder Structure

```
recipe-site/
├── scripts/
│   ├── scrape_recipes.py      # Extract recipes from Safari Reading List
│   └── generate_site.py       # Build static site
├── site/                      # Generated website (DO NOT EDIT)
├── data/
│   └── recipes.json           # Scraped recipe data
├── .github/workflows/
│   └── deploy.yml             # Automation workflow
└── requirements.txt           # Python dependencies
```

## Customization

Edit `scripts/generate_site.py` to customize:
- Colors and styling
- Layout and design
- Additional features

## Troubleshooting

**Recipe not scraping correctly?**
- Some sites may not be supported by recipe-scrapers
- Check `data/recipes.json` for error messages
- You can manually add recipes to this JSON file

**Site not updating?**
- Check GitHub Actions tab for build logs
- Ensure Bookmarks.html is in the data/ folder
- Verify GitHub Pages is enabled in repository settings
