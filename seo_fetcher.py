import random
import json
import os
from typing import Dict, Any

def get_seo_data(keyword: str) -> Dict[str, Any]:
    """
    Fetch SEO data for a given keyword.
    For this demo, we're using mock data, but this could be replaced
    with real API calls to services like SEMrush, Ahrefs, or Google Keyword Planner.
    """
    
    # Check if we have cached mock data
    mock_data_file = 'mock_seo_data.json'
    
    if os.path.exists(mock_data_file):
        with open(mock_data_file, 'r') as f:
            mock_database = json.load(f)
        
        # Check if we have data for this specific keyword
        if keyword.lower() in mock_database:
            return mock_database[keyword.lower()]
    
    # Generate realistic mock data based on keyword characteristics
    seo_data = generate_mock_seo_data(keyword)
    
    return seo_data

def generate_mock_seo_data(keyword: str) -> Dict[str, Any]:
    """Generate random mock SEO data based on keyword characteristics"""
    
    # Keyword length and type affect metrics
    word_count = len(keyword.split())
    
    # Longer, more specific keywords typically have lower search volume but lower difficulty
    if word_count >= 4:  # Long-tail keywords
        search_volume = random.randint(100, 2000)
        keyword_difficulty = random.randint(15, 45)
        avg_cpc = round(random.uniform(0.50, 3.50), 2)
    elif word_count == 3:  # Medium-tail keywords
        search_volume = random.randint(1000, 8000)
        keyword_difficulty = random.randint(35, 65)
        avg_cpc = round(random.uniform(1.50, 6.00), 2)
    else:  # Short, broad keywords (1-2 words)
        search_volume = random.randint(5000, 50000)
        keyword_difficulty = random.randint(60, 95)
        avg_cpc = round(random.uniform(3.00, 15.00), 2)
    
    # Adjust based on keyword type
    commercial_keywords = ['buy', 'best', 'review', 'price', 'cheap', 'discount', 'deal']
    informational_keywords = ['how', 'what', 'why', 'guide', 'tutorial', 'tips']
    
    keyword_lower = keyword.lower()
    
    if any(word in keyword_lower for word in commercial_keywords):
        # Commercial keywords have higher CPC
        avg_cpc *= random.uniform(1.5, 2.5)
        search_volume = int(search_volume * random.uniform(0.8, 1.2))
    elif any(word in keyword_lower for word in informational_keywords):
        # Informational keywords have lower CPC
        avg_cpc *= random.uniform(0.3, 0.8)
        search_volume = int(search_volume * random.uniform(1.2, 1.8))
    
    # Generate related keywords
    related_keywords = generate_related_keywords(keyword)
    
    # Generate top ranking pages (mock data)
    top_pages = [
        {
            "url": f"https://example{i}.com/article-about-{keyword.replace(' ', '-')}",
            "title": f"Ultimate Guide to {keyword.title()} - Top {random.randint(5, 15)} Picks",
            "domain_authority": random.randint(40, 90)
        } for i in range(1, 6)
    ]
    
    return {
        "keyword": keyword,
        "search_volume": search_volume,
        "keyword_difficulty": keyword_difficulty,
        "avg_cpc": round(avg_cpc, 2),
        "related_keywords": related_keywords,
        "top_ranking_pages": top_pages,
        "search_trends": generate_search_trends(),
        "competition_level": get_competition_level(keyword_difficulty),
        "suggested_bid": round(avg_cpc * random.uniform(0.8, 1.2), 2)
    }

def generate_related_keywords(main_keyword: str) -> list:
    """Generate related keywords based on the main keyword"""
    base_modifiers = [
        "best", "top", "review", "guide", "how to", "cheap", "discount",
        "2024", "2025", "buy", "price", "vs", "comparison", "alternative"
    ]
    
    related = []
    words = main_keyword.split()
    
    # Add modifiers to the main keyword
    for modifier in random.sample(base_modifiers, min(5, len(base_modifiers))):
        if modifier in ["how to"]:
            related.append(f"{modifier} choose {main_keyword}")
        elif modifier in ["vs", "comparison"]:
            related.append(f"{main_keyword} {modifier}")
        else:
            related.append(f"{modifier} {main_keyword}")
    
    # Add some variations
    if len(words) > 1:
        # Swap word order for some variations
        related.append(" ".join(reversed(words)))
    
    return related[:8]  # Return top 8 related keywords

def generate_search_trends() -> Dict[str, int]:
    """Generate mock search trend data for the last 12 months"""
    months = [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
    ]
    
    # Generate trending data with some seasonality
    base_volume = random.randint(70, 100)
    trends = {}
    
    for month in months:
        # Add some random variation
        variation = random.randint(-20, 30)
        trends[month] = max(10, base_volume + variation)
    
    return trends

def get_competition_level(difficulty_score: int) -> str:
    """Convert difficulty score to human-readable competition level"""
    if difficulty_score < 30:
        return "Low"
    elif difficulty_score < 60:
        return "Medium"
    else:
        return "High"

# Create mock database for consistent results during testing
def create_mock_database():
    """Create a mock database for testing purposes"""
    test_keywords = [
        "wireless earbuds", "best headphones", "laptop reviews",
        "gaming mouse", "smartphone 2024", "fitness tracker",
        "coffee maker", "air fryer recipes", "yoga mat",
        "running shoes"
    ]
    
    mock_db = {}
    for keyword in test_keywords:
        mock_db[keyword.lower()] = generate_mock_seo_data(keyword)
    
    with open('mock_seo_data.json', 'w') as f:
        json.dump(mock_db, f, indent=2)

if __name__ == "__main__":
    # Create mock database when run directly
    create_mock_database()
    print("Mock SEO database created!")
    
    # Test the function
    test_keyword = "wireless earbuds"
    data = get_seo_data(test_keyword)
    print(f"\nSample SEO data for '{test_keyword}':")
    print(json.dumps(data, indent=2))