#!/usr/bin/env python3
"""
Static Site Generator
Builds the recipe website from recipes.json
"""

import json
import os
from pathlib import Path
from datetime import datetime

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
RECIPES_FILE = DATA_DIR / "recipes.json"
SITE_DIR = BASE_DIR / "site"

def load_recipes():
    """Load recipes from JSON file"""
    if not RECIPES_FILE.exists():
        print(f"❌ Error: {RECIPES_FILE} not found")
        print("Run 'python scripts/scrape_recipes.py' first")
        return []
    
    with open(RECIPES_FILE, 'r', encoding='utf-8') as f:
        recipes = json.load(f)
    
    # Filter out failed scrapes
    successful_recipes = [r for r in recipes if r.get('scraped_successfully')]
    print(f"📚 Loaded {len(successful_recipes)} recipes")
    return successful_recipes

def generate_recipe_card_html(recipe, index):
    """Generate HTML for a single recipe card"""
    image_url = recipe.get('image') or 'https://via.placeholder.com/400x300?text=No+Image'
    title = recipe.get('title', 'Untitled Recipe')
    host = recipe.get('host', '')
    total_time = recipe.get('total_time', 0)
    yields = recipe.get('yields', '')
    
    time_str = f"{total_time} min" if total_time else ""
    
    return f'''
    <div class="recipe-card" data-index="{index}">
        <img src="{image_url}" alt="{title}" loading="lazy" onerror="this.src='https://via.placeholder.com/400x300?text=No+Image'">
        <div class="recipe-card-content">
            <h3>{title}</h3>
            <div class="recipe-meta">
                <span class="recipe-source">{host}</span>
                {f'<span class="recipe-time">⏱️ {time_str}</span>' if time_str else ''}
                {f'<span class="recipe-yields">🍽️ {yields}</span>' if yields else ''}
            </div>
        </div>
    </div>
    '''

def generate_recipe_detail_html(recipe, index):
    """Generate HTML for recipe detail view"""
    ingredients_html = ''.join([f'<li>{ing}</li>' for ing in recipe.get('ingredients', [])])
    instructions = recipe.get('instructions', 'No instructions available')
    
    return f'''
    <div class="recipe-detail" id="recipe-{index}" style="display: none;">
        <button class="back-btn" onclick="closeRecipe()">← Back</button>
        <h2>{recipe.get('title', 'Untitled Recipe')}</h2>
        
        <div class="recipe-image-container">
            <img src="{recipe.get('image') or 'https://via.placeholder.com/800x600?text=No+Image'}" 
                 alt="{recipe.get('title', '')}"
                 onerror="this.src='https://via.placeholder.com/800x600?text=No+Image'">
        </div>
        
        <div class="recipe-info">
            {f'<div class="info-item"><strong>Time:</strong> {recipe.get("total_time")} min</div>' if recipe.get('total_time') else ''}
            {f'<div class="info-item"><strong>Servings:</strong> {recipe.get("yields")}</div>' if recipe.get('yields') else ''}
            {f'<div class="info-item"><strong>Author:</strong> {recipe.get("author")}</div>' if recipe.get('author') and recipe.get('author') != 'Unknown' else ''}
        </div>
        
        <div class="recipe-section">
            <h3>Ingredients</h3>
            <ul class="ingredients-list">
                {ingredients_html}
            </ul>
        </div>
        
        <div class="recipe-section">
            <h3>Instructions</h3>
            <div class="instructions">
                {instructions.replace(chr(10), '<br><br>')}
            </div>
        </div>
        
        <div class="recipe-footer">
            <a href="{recipe.get('url')}" target="_blank" class="source-link">View Original Recipe →</a>
        </div>
    </div>
    '''

def generate_html(recipes):
    """Generate the complete HTML page"""
    
    recipe_cards = '\n'.join([generate_recipe_card_html(r, i) for i, r in enumerate(recipes)])
    recipe_details = '\n'.join([generate_recipe_detail_html(r, i) for i, r in enumerate(recipes)])
    
    # Create recipes JSON for search functionality
    recipes_json = json.dumps([{
        'title': r.get('title', ''),
        'host': r.get('host', ''),
        'ingredients': r.get('ingredients', []),
        'category': r.get('category', ''),
        'cuisine': r.get('cuisine', ''),
    } for r in recipes])
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Recipe Collection</title>
    <meta name="description" content="Personal recipe collection - {len(recipes)} recipes">
    
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        :root {{
            --primary: #2563eb;
            --primary-dark: #1e40af;
            --bg: #f8fafc;
            --card-bg: #ffffff;
            --text: #1e293b;
            --text-light: #64748b;
            --border: #e2e8f0;
            --shadow: 0 1px 3px rgba(0,0,0,0.1);
            --shadow-lg: 0 10px 25px rgba(0,0,0,0.1);
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
        }}
        
        .header {{
            background: var(--card-bg);
            padding: 1rem;
            box-shadow: var(--shadow);
            position: sticky;
            top: 0;
            z-index: 100;
        }}
        
        .header-content {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        h1 {{
            font-size: 1.5rem;
            margin-bottom: 0.5rem;
        }}
        
        .search-bar {{
            width: 100%;
            padding: 0.75rem;
            border: 1px solid var(--border);
            border-radius: 8px;
            font-size: 1rem;
            margin-top: 0.5rem;
        }}
        
        .search-bar:focus {{
            outline: none;
            border-color: var(--primary);
        }}
        
        .recipe-count {{
            color: var(--text-light);
            font-size: 0.875rem;
            margin-top: 0.5rem;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 1rem;
        }}
        
        .recipes-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 1.5rem;
            margin-top: 1rem;
        }}
        
        .recipe-card {{
            background: var(--card-bg);
            border-radius: 12px;
            overflow: hidden;
            box-shadow: var(--shadow);
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .recipe-card:hover {{
            transform: translateY(-2px);
            box-shadow: var(--shadow-lg);
        }}
        
        .recipe-card img {{
            width: 100%;
            height: 200px;
            object-fit: cover;
        }}
        
        .recipe-card-content {{
            padding: 1rem;
        }}
        
        .recipe-card h3 {{
            font-size: 1.125rem;
            margin-bottom: 0.5rem;
            color: var(--text);
        }}
        
        .recipe-meta {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            font-size: 0.875rem;
            color: var(--text-light);
        }}
        
        .recipe-source {{
            font-weight: 500;
        }}
        
        .recipe-detail {{
            max-width: 800px;
            margin: 0 auto;
            background: var(--card-bg);
            border-radius: 12px;
            padding: 2rem;
            box-shadow: var(--shadow-lg);
        }}
        
        .back-btn {{
            background: var(--primary);
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1rem;
            margin-bottom: 1rem;
        }}
        
        .back-btn:hover {{
            background: var(--primary-dark);
        }}
        
        .recipe-detail h2 {{
            font-size: 2rem;
            margin-bottom: 1rem;
        }}
        
        .recipe-image-container {{
            margin: 1.5rem 0;
            border-radius: 12px;
            overflow: hidden;
        }}
        
        .recipe-image-container img {{
            width: 100%;
            height: auto;
            display: block;
        }}
        
        .recipe-info {{
            display: flex;
            flex-wrap: wrap;
            gap: 1rem;
            padding: 1rem;
            background: var(--bg);
            border-radius: 8px;
            margin: 1.5rem 0;
        }}
        
        .info-item {{
            flex: 1;
            min-width: 150px;
        }}
        
        .recipe-section {{
            margin: 2rem 0;
        }}
        
        .recipe-section h3 {{
            font-size: 1.5rem;
            margin-bottom: 1rem;
            color: var(--text);
        }}
        
        .ingredients-list {{
            list-style: none;
            padding: 0;
        }}
        
        .ingredients-list li {{
            padding: 0.5rem 0;
            border-bottom: 1px solid var(--border);
        }}
        
        .ingredients-list li:last-child {{
            border-bottom: none;
        }}
        
        .instructions {{
            line-height: 1.8;
            font-size: 1.05rem;
        }}
        
        .recipe-footer {{
            margin-top: 2rem;
            padding-top: 1rem;
            border-top: 1px solid var(--border);
        }}
        
        .source-link {{
            color: var(--primary);
            text-decoration: none;
            font-weight: 500;
        }}
        
        .source-link:hover {{
            text-decoration: underline;
        }}
        
        .no-results {{
            text-align: center;
            padding: 4rem 1rem;
            color: var(--text-light);
        }}
        
        @media (max-width: 768px) {{
            .recipes-grid {{
                grid-template-columns: 1fr;
            }}
            
            .recipe-detail {{
                padding: 1rem;
            }}
            
            .recipe-detail h2 {{
                font-size: 1.5rem;
            }}
        }}
    </style>
</head>
<body>
    <header class="header">
        <div class="header-content">
            <h1>🍳 My Recipe Collection</h1>
            <input type="text" id="searchInput" class="search-bar" placeholder="Search recipes...">
            <div class="recipe-count" id="recipeCount">{len(recipes)} recipes</div>
        </div>
    </header>
    
    <div class="container">
        <div class="recipes-grid" id="recipesGrid">
            {recipe_cards}
        </div>
        
        <div id="recipeDetail" style="display: none;">
            {recipe_details}
        </div>
        
        <div class="no-results" id="noResults" style="display: none;">
            <h2>No recipes found</h2>
            <p>Try a different search term</p>
        </div>
    </div>
    
    <script>
        const recipesData = {recipes_json};
        
        // Search functionality
        const searchInput = document.getElementById('searchInput');
        const recipesGrid = document.getElementById('recipesGrid');
        const recipeCards = document.querySelectorAll('.recipe-card');
        const recipeCount = document.getElementById('recipeCount');
        const noResults = document.getElementById('noResults');
        
        searchInput.addEventListener('input', (e) => {{
            const searchTerm = e.target.value.toLowerCase();
            let visibleCount = 0;
            
            recipeCards.forEach((card, index) => {{
                const recipe = recipesData[index];
                const searchableText = [
                    recipe.title,
                    recipe.host,
                    recipe.category || '',
                    recipe.cuisine || '',
                    ...recipe.ingredients
                ].join(' ').toLowerCase();
                
                if (searchableText.includes(searchTerm)) {{
                    card.style.display = 'block';
                    visibleCount++;
                }} else {{
                    card.style.display = 'none';
                }}
            }});
            
            recipeCount.textContent = `${{visibleCount}} recipe${{visibleCount !== 1 ? 's' : ''}}`;
            noResults.style.display = visibleCount === 0 ? 'block' : 'none';
            recipesGrid.style.display = visibleCount === 0 ? 'none' : 'grid';
        }});
        
        // Recipe card click handlers
        recipeCards.forEach((card) => {{
            card.addEventListener('click', () => {{
                const index = card.dataset.index;
                openRecipe(index);
            }});
        }});
        
        function openRecipe(index) {{
            recipesGrid.style.display = 'none';
            document.getElementById('recipeDetail').style.display = 'block';
            document.getElementById(`recipe-${{index}}`).style.display = 'block';
            window.scrollTo(0, 0);
        }}
        
        function closeRecipe() {{
            document.getElementById('recipeDetail').style.display = 'none';
            document.querySelectorAll('.recipe-detail').forEach(detail => {{
                detail.style.display = 'none';
            }});
            recipesGrid.style.display = 'grid';
        }}
        
        // Update last generated time
        console.log('Site generated: {datetime.now().isoformat()}');
    </script>
</body>
</html>'''
    
    return html

def main():
    recipes = load_recipes()
    
    if not recipes:
        print("❌ No recipes to generate site from")
        return
    
    # Create site directory
    SITE_DIR.mkdir(parents=True, exist_ok=True)
    
    # Generate HTML
    html = generate_html(recipes)
    
    # Write index.html
    index_file = SITE_DIR / 'index.html'
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ Site generated at {index_file}")
    print(f"📊 {len(recipes)} recipes included")
    print(f"\n🌐 Test locally: python -m http.server 8000 --directory site")
    print(f"   Then open: http://localhost:8000")

if __name__ == '__main__':
    main()
