#!/usr/bin/env python3
"""
Recipe Scraper
Extracts recipes from Safari Reading List and saves to JSON
"""

import json
import os
import plistlib
from pathlib import Path
from urllib.parse import urlparse
from recipe_scrapers import scrape_html
import requests
import time

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
SAFARI_BOOKMARKS = Path.home() / "Library/Safari/Bookmarks.plist"
OUTPUT_FILE = DATA_DIR / "recipes.json"

def extract_urls_from_safari_reading_list():
    """
    Extract URLs from Safari's Reading List by reading the Bookmarks.plist file
    """
    if not SAFARI_BOOKMARKS.exists():
        print(f"❌ Safari bookmarks file not found at: {SAFARI_BOOKMARKS}")
        print("This script needs to run on a Mac with Safari.")
        return []
    
    print(f"📖 Reading Safari Reading List from {SAFARI_BOOKMARKS}")
    
    try:
        with open(SAFARI_BOOKMARKS, 'rb') as f:
            plist = plistlib.load(f)
    except Exception as e:
        print(f"❌ Error reading Safari bookmarks: {e}")
        return []
    
    urls = []
    
    # Safari stores Reading List in the bookmarks structure
    # We need to find the "com.apple.ReadingList" folder
    def find_reading_list(item):
        """Recursively search for Reading List items"""
        if isinstance(item, dict):
            # Check if this is the Reading List folder
            if item.get('Title') == 'com.apple.ReadingList':
                return item.get('Children', [])
            
            # Check if this item has children to search
            if 'Children' in item:
                for child in item['Children']:
                    result = find_reading_list(child)
                    if result:
                        return result
        
        return None
    
    # Start searching from the root
    reading_list_items = find_reading_list(plist)
    
    if not reading_list_items:
        print("⚠️  No Reading List found in Safari bookmarks")
        return []
    
    # Extract URLs from Reading List items
    for item in reading_list_items:
        if isinstance(item, dict) and 'URLString' in item:
            url = item['URLString']
            title = item.get('URIDictionary', {}).get('title', '') or item.get('ReadingList', {}).get('Title', 'Untitled')
            
            urls.append({
                'url': url,
                'bookmark_title': title
            })
    
    print(f"✅ Found {len(urls)} URLs in Reading List")
    return urls

def scrape_recipe(url, bookmark_title):
    """
    Scrape a single recipe from a URL
    """
    try:
        print(f"  Scraping: {url[:60]}...")
        
        # Fetch the HTML
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Use recipe-scrapers library
        scraper = scrape_html(html=response.content, org_url=url)
        
        recipe = {
            'title': scraper.title(),
            'url': url,
            'bookmark_title': bookmark_title,
            'host': scraper.host(),
            'total_time': scraper.total_time(),
            'yields': scraper.yields(),
            'ingredients': scraper.ingredients(),
            'instructions': scraper.instructions(),
            'image': scraper.image(),
            'author': scraper.author() if hasattr(scraper, 'author') else 'Unknown',
            'cuisine': scraper.cuisine() if hasattr(scraper, 'cuisine') else None,
            'category': scraper.category() if hasattr(scraper, 'category') else None,
            'scraped_successfully': True,
            'error': None
        }
        
        print(f"  ✅ {recipe['title']}")
        return recipe
        
    except Exception as e:
        print(f"  ❌ Failed: {str(e)[:100]}")
        return {
            'title': bookmark_title or 'Unknown Recipe',
            'url': url,
            'bookmark_title': bookmark_title,
            'host': urlparse(url).netloc,
            'scraped_successfully': False,
            'error': str(e)
        }

def scrape_all_recipes(bookmarks):
    """
    Scrape all recipes from bookmark list
    """
    recipes = []
    total = len(bookmarks)
    
    print(f"\n🔄 Starting to scrape {total} recipes...\n")
    
    for i, bookmark in enumerate(bookmarks, 1):
        print(f"[{i}/{total}]", end=" ")
        recipe = scrape_recipe(bookmark['url'], bookmark['bookmark_title'])
        recipes.append(recipe)
        
        # Be polite to servers - add delay between requests
        time.sleep(1)
    
    successful = sum(1 for r in recipes if r.get('scraped_successfully'))
    print(f"\n✅ Successfully scraped {successful}/{total} recipes")
    
    return recipes

def save_recipes(recipes, output_file):
    """
    Save recipes to JSON file
    """
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(recipes, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Saved recipes to {output_file}")

def main():
    # Extract URLs from Safari Reading List
    bookmarks = extract_urls_from_safari_reading_list()
    
    if not bookmarks:
        print("❌ No URLs found in Safari Reading List")
        print("\nMake sure you're running this on a Mac with Safari installed.")
        print("Your Reading List items should be at: ~/Library/Safari/Bookmarks.plist")
        return
    
    # Scrape all recipes
    recipes = scrape_all_recipes(bookmarks)
    
    # Save to JSON
    save_recipes(recipes, OUTPUT_FILE)
    
    print("\n🎉 Done! Run 'python scripts/generate_site.py' to build the website.")

if __name__ == '__main__':
    main()
