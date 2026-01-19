# How Automatic Updates Work

## The Workflow

Since the scraper needs to run on your Mac (to access Safari's Reading List), the GitHub Actions workflow has been simplified to just **deploy** the site, not scrape recipes.

Here's how it works:

```
Your Mac                          GitHub
---------                         --------
1. Add recipes to Safari
2. Run scraper locally      →     
3. Commit recipes.json      →     4. Auto-deploy site
                                  5. Site live at github.io
```

## Setting Up Automatic Local Scraping

### Option 1: Manual (Recommended to Start)

When you want to update:
```bash
cd ~/Documents/recipe-site
source venv/bin/activate
python scripts/scrape_recipes.py
python scripts/generate_site.py
git add data/recipes.json site/
git commit -m "Updated recipes"
git push
```

### Option 2: Cron Job (Fully Automatic)

To have your Mac automatically scrape and push updates daily:

1. Create a script at `~/recipe-update.sh`:

```bash
#!/bin/bash
cd ~/Documents/recipe-site
source venv/bin/activate

# Scrape new recipes
python scripts/scrape_recipes.py

# Generate site
python scripts/generate_site.py

# Check if there are changes
if [[ -n $(git status -s data/recipes.json) ]]; then
    git add data/recipes.json site/
    git commit -m "Auto-update recipes $(date +%Y-%m-%d)"
    git push
    echo "✅ Recipes updated and pushed"
else
    echo "No new recipes found"
fi
```

2. Make it executable:
```bash
chmod +x ~/recipe-update.sh
```

3. Add to crontab (runs daily at 3 AM):
```bash
crontab -e

# Add this line:
0 3 * * * ~/recipe-update.sh >> ~/recipe-update.log 2>&1
```

### Option 3: GitHub Self-Hosted Runner (Advanced)

For true automation, you can set up a GitHub self-hosted runner on your Mac. This allows GitHub Actions to run on your machine and access Safari's Reading List.

See: https://docs.github.com/en/actions/hosting-your-own-runners

## Why This Approach?

Safari's Reading List data (`~/Library/Safari/Bookmarks.plist`) is only accessible on your Mac. GitHub Actions runners are Linux/Windows machines without access to your Safari data.

**Alternative Approaches:**
1. **Cloud sync**: Copy `Bookmarks.plist` to Dropbox/iCloud and access it from GitHub Actions (security concerns)
2. **API**: Use iCloud API to access Reading List (complex, requires authentication)
3. **Self-hosted runner**: Best for true automation (requires Mac to be always on)

The simplest solution is running the scraper locally and committing the `recipes.json` file.
