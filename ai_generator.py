import os
import openai
from typing import Dict, Any
import random
import re
from datetime import datetime

# Initialize OpenAI client
openai.api_key = os.getenv('OPENAI_API_KEY')

def generate_blog_post(keyword: str, seo_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a blog post using OpenAI API based on keyword and SEO data
    """
    
    if not openai.api_key:
        print("Warning: OpenAI API key not found. Using fallback content.")
        return generate_fallback_content(keyword, seo_data)
    
    # Create the prompt
    prompt = create_blog_post_prompt(keyword, seo_data)
    
    try:
        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert SEO content writer and affiliate marketer. Create engaging, informative blog posts that rank well in search engines and naturally incorporate affiliate links. Return ONLY clean HTML content without any markdown code blocks or extra formatting."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=2500,
            temperature=0.7
        )
        
        raw_content = response.choices[0].message.content.strip()
        
        # Clean up any markdown formatting issues
        raw_content = clean_markdown_artifacts(raw_content)
        
        # Process the content to add affiliate links and structure
        processed_content = process_blog_content(raw_content, keyword)
        
        return {
            "title": extract_title(processed_content),
            "content": processed_content,
            "word_count": len(re.sub(r'<[^>]+>', '', processed_content).split()),
            "meta_description": generate_meta_description(keyword, processed_content),
            "tags": generate_tags(keyword, seo_data),
            "estimated_reading_time": calculate_reading_time(processed_content)
        }
        
    except Exception as e:
        print(f"Error with OpenAI API: {str(e)}. Using fallback content.")
        return generate_fallback_content(keyword, seo_data)

def clean_markdown_artifacts(content: str) -> str:
    """Remove markdown code block artifacts and fix formatting issues"""
    # Remove markdown code blocks
    content = re.sub(r'```html\s*', '', content)
    content = re.sub(r'```\s*', '', content)
    
    # Remove duplicate DOCTYPE and HTML tags
    content = re.sub(r'<!DOCTYPE html>\s*<html[^>]*>\s*<head>.*?</head>\s*<body>\s*<!DOCTYPE html>', '<!DOCTYPE html>', content, flags=re.DOTALL)
    content = re.sub(r'</body>\s*</html>\s*$', '', content)
    
    # Clean up any remaining artifacts
    content = content.strip()
    
    return content

def create_blog_post_prompt(keyword: str, seo_data: Dict[str, Any]) -> str:
    """Create a detailed prompt for the OpenAI API"""
    
    related_keywords = ", ".join(seo_data.get('related_keywords', [])[:5])
    
    prompt = f"""
Write a comprehensive, SEO-optimized blog post about "{keyword}".

SEO Data Context:
- Search Volume: {seo_data.get('search_volume', 'N/A')}
- Keyword Difficulty: {seo_data.get('keyword_difficulty', 'N/A')}
- Competition Level: {seo_data.get('competition_level', 'Medium')}
- Related Keywords: {related_keywords}

Requirements:
1. Create an engaging title with the main keyword
2. Write a compelling introduction that hooks the reader
3. Structure the content with clear H2 and H3 headings
4. Include the main keyword naturally throughout (aim for 1-2% density)
5. Incorporate related keywords naturally
6. Add 3-5 placeholder affiliate links using the format {{{{AFF_LINK_1}}}}, {{{{AFF_LINK_2}}}}, etc.
7. Include a FAQ section with 3-4 common questions
8. End with a compelling conclusion that encourages action
9. Make it approximately 1500-2000 words
10. Use HTML formatting for structure

Content Style:
- Write in a friendly, authoritative tone
- Use bullet points and numbered lists where appropriate
- Include practical tips and actionable advice
- Make it valuable for readers searching for "{keyword}"
- Naturally mention product features, benefits, and comparisons

IMPORTANT: Return ONLY the HTML content without any markdown code blocks, backticks, or extra formatting. Start directly with the HTML content.
"""
    
    return prompt

def process_blog_content(content: str, keyword: str) -> str:
    """Process the blog content to add affiliate links and improve structure"""
    
    # Define affiliate link placeholders and their replacements
    affiliate_links = {
        '{{AFF_LINK_1}}': 'https://amazon.com/affiliate/product1?tag=yourtag',
        '{{AFF_LINK_2}}': 'https://amazon.com/affiliate/product2?tag=yourtag',
        '{{AFF_LINK_3}}': 'https://amazon.com/affiliate/product3?tag=yourtag',
        '{{AFF_LINK_4}}': 'https://bestbuy.com/affiliate/product4?tag=yourtag',
        '{{AFF_LINK_5}}': 'https://walmart.com/affiliate/product5?tag=yourtag'
    }
    
    # Replace affiliate link placeholders
    for placeholder, link in affiliate_links.items():
        content = content.replace(placeholder, link)
    
    # Ensure proper HTML structure
    if not content.strip().startswith('<!DOCTYPE html>'):
        # Wrap content in proper HTML structure
        title = extract_title_text(content) or f"{keyword.title()} - Expert Guide"
        content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }}
        h1, h2, h3 {{ color: #333; }}
        a {{ color: #007bff; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        .faq {{ margin-top: 30px; }}
        .faq h3 {{ margin-top: 20px; }}
    </style>
</head>
<body>
{content}
</body>
</html>"""
    
    return content

def extract_title(content: str) -> str:
    """Extract the main title from the content"""
    # Look for h1 tag first
    h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', content, re.IGNORECASE | re.DOTALL)
    if h1_match:
        return h1_match.group(1).strip()
    
    # Look for first heading
    heading_match = re.search(r'<h[1-6][^>]*>(.*?)</h[1-6]>', content, re.IGNORECASE | re.DOTALL)
    if heading_match:
        return heading_match.group(1).strip()
    
    # Look for title tag
    title_match = re.search(r'<title[^>]*>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
    if title_match:
        return title_match.group(1).strip()
    
    # Fallback to first line if no headings found
    lines = content.split('\n')
    for line in lines:
        clean_line = re.sub(r'<[^>]+>', '', line).strip()
        if clean_line and len(clean_line) > 10:
            return clean_line[:100] + ('...' if len(clean_line) > 100 else '')
    
    return "Generated Blog Post"

def extract_title_text(content: str) -> str:
    """Extract clean title text without HTML tags"""
    title = extract_title(content)
    return re.sub(r'<[^>]+>', '', title).strip()

def generate_meta_description(keyword: str, content: str) -> str:
    """Generate a meta description based on the content"""
    # Remove HTML tags for processing
    clean_content = re.sub(r'<[^>]+>', '', content)
    
    # Find the first paragraph that mentions the keyword
    paragraphs = [p.strip() for p in clean_content.split('\n') if p.strip()]
    
    for paragraph in paragraphs[:5]:  # Check first 5 paragraphs
        if keyword.lower() in paragraph.lower() and len(paragraph) > 50:
            # Truncate to meta description length
            description = paragraph[:155]
            if len(paragraph) > 155:
                description = description.rsplit(' ', 1)[0] + '...'
            return description
    
    # Fallback generic description
    return f"Discover everything you need to know about {keyword}. Expert reviews, comparisons, and buying guides to help you make the best choice."

def generate_tags(keyword: str, seo_data: Dict[str, Any]) -> list:
    """Generate relevant tags for the blog post"""
    tags = [keyword]
    
    # Add related keywords as tags
    related = seo_data.get('related_keywords', [])
    tags.extend(related[:5])
    
    # Add some generic relevant tags
    generic_tags = ['review', 'guide', 'buying guide', '2024', 'best']
    tags.extend([tag for tag in generic_tags if tag not in ' '.join(tags).lower()])
    
    return tags[:10]  # Limit to 10 tags

def calculate_reading_time(content: str) -> str:
    """Calculate estimated reading time based on word count"""
    # Remove HTML tags for word count
    clean_content = re.sub(r'<[^>]+>', '', content)
    word_count = len(clean_content.split())
    
    # Average reading speed is 200-250 words per minute
    reading_time = max(1, round(word_count / 225))
    
    return f"{reading_time} min read"

def generate_fallback_content(keyword: str, seo_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate fallback content if OpenAI API fails"""
    
    title = f"The Ultimate Guide to {keyword.title()}: Everything You Need to Know"
    
    content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }}
        h1, h2, h3 {{ color: #333; }}
        a {{ color: #007bff; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        .faq {{ margin-top: 30px; }}
        .faq h3 {{ margin-top: 20px; }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    
    <p>Welcome to our comprehensive guide about <strong>{keyword}</strong>. In this article, we'll cover everything you need to know to make an informed decision.</p>
    
    <h2>What Makes Great {keyword.title()}?</h2>
    <p>When looking for the best {keyword}, there are several key factors to consider:</p>
    <ul>
        <li>Quality and durability</li>
        <li>Value for money</li>
        <li>User reviews and ratings</li>
        <li>Brand reputation</li>
        <li>Warranty and support</li>
    </ul>
    
    <h2>Top Recommendations</h2>
    <p>Based on our research and testing, here are our top picks for {keyword}:</p>
    
    <h3>1. Premium Choice</h3>
    <p>For those looking for the best quality, we recommend checking out <a href="https://amazon.com/affiliate/product1?tag=yourtag" target="_blank" rel="noopener">this premium option</a>.</p>
    
    <h3>2. Best Value</h3>
    <p>If you're looking for great value, <a href="https://amazon.com/affiliate/product2?tag=yourtag" target="_blank" rel="noopener">this budget-friendly choice</a> offers excellent features at an affordable price.</p>
    
    <h2>Buying Guide</h2>
    <p>Here's what to look for when shopping for {keyword}:</p>
    <ol>
        <li>Set your budget range</li>
        <li>Read customer reviews</li>
        <li>Compare features</li>
        <li>Check warranty terms</li>
        <li>Consider future needs</li>
    </ol>
    
    <div class="faq">
        <h2>Frequently Asked Questions</h2>
        
        <h3>What's the best {keyword} for beginners?</h3>
        <p>For beginners, we recommend starting with <a href="https://amazon.com/affiliate/product3?tag=yourtag" target="_blank" rel="noopener">this user-friendly option</a> that offers great features without overwhelming complexity.</p>
        
        <h3>How much should I spend on {keyword}?</h3>
        <p>The price range varies widely, but you can find quality options starting from budget-friendly to premium levels. Consider your specific needs and budget.</p>
        
        <h3>Are there any special features I should look for?</h3>
        <p>Look for features that match your specific use case, such as durability, ease of use, and compatibility with your existing setup.</p>
    </div>
    
    <h2>Conclusion</h2>
    <p>Choosing the right {keyword} doesn't have to be complicated. By considering the factors we've outlined and checking out our recommended options, you'll be well on your way to making the perfect choice for your needs.</p>
    
    <p><em>Last updated: {datetime.now().strftime('%B %Y')}</em></p>
</body>
</html>"""
    
    return {
        "title": title,
        "content": content,
        "word_count": len(re.sub(r'<[^>]+>', '', content).split()),  # Clean word count
        "meta_description": f"Complete guide to {keyword}. Expert recommendations, buying tips, and reviews to help you choose the best {keyword} for your needs.",
        "tags": generate_tags(keyword, seo_data),
        "estimated_reading_time": calculate_reading_time(content)
    }

def save_blog_post(blog_post_data: Dict[str, Any], keyword: str, output_dir: str = "generated_posts") -> str:
    """Save blog post to files"""
    import os
    import json
    from datetime import datetime
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_keyword = keyword.replace(' ', '_').replace('/', '_')
    
    # Save HTML file
    html_filename = f"{output_dir}/{safe_keyword}_{timestamp}.html"
    with open(html_filename, 'w', encoding='utf-8') as f:
        f.write(blog_post_data['content'])
    
    # Save JSON metadata
    json_filename = f"{output_dir}/{safe_keyword}_{timestamp}.json"
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(blog_post_data, f, indent=2, ensure_ascii=False)
    
    return html_filename

if __name__ == "__main__":
    # Test the function with mock data
    test_keyword = "wireless earbuds"
    test_seo_data = {
        "search_volume": 10000,
        "keyword_difficulty": 45,
        "competition_level": "Medium",
        "related_keywords": ["best wireless earbuds", "bluetooth earbuds", "noise canceling earbuds"]
    }
    
    try:
        result = generate_blog_post(test_keyword, test_seo_data)
        print("Blog post generated successfully!")
        print(f"Title: {result['title']}")
        print(f"Word count: {result['word_count']}")
        print(f"Reading time: {result['estimated_reading_time']}")
        
        # Save the generated post
        saved_file = save_blog_post(result, test_keyword)
        print(f"Blog post saved to: {saved_file}")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Generating fallback content...")
        result = generate_fallback_content(test_keyword, test_seo_data)
        print(f"Fallback title: {result['title']}")
        print(f"Fallback word count: {result['word_count']}")
        saved_file = save_blog_post(result, test_keyword)
        print(f"Fallback blog post saved to: {saved_file}")