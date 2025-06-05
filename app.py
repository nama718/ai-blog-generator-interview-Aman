from flask import Flask, request, jsonify, send_file
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()
import os
import json
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import atexit
from seo_fetcher import get_seo_data
from ai_generator import generate_blog_post, save_blog_post
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize scheduler
scheduler = BackgroundScheduler()
scheduler.start()

# Ensure scheduler shuts down when the app exits
atexit.register(lambda: scheduler.shutdown())

@app.route('/')
def home():
    return jsonify({
        "message": "AI Blog Post Generator API",
        "endpoints": {
            "/generate": "GET - Generate blog post with ?keyword=<keyword>&save=true (optional)",
            "/posts": "GET - List generated posts",
            "/posts/<filename>": "GET - View specific post",
            "/health": "GET - Health check"
        }
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route('/generate')
def generate():
    keyword = request.args.get('keyword')
    save_post = request.args.get('save', 'false').lower() == 'true'
    
    if not keyword:
        return jsonify({"error": "keyword parameter is required"}), 400
    
    try:
        # Get SEO data
        logger.info(f"Fetching SEO data for keyword: {keyword}")
        seo_data = get_seo_data(keyword)
        
        # Generate blog post
        logger.info(f"Generating blog post for keyword: {keyword}")
        blog_post = generate_blog_post(keyword, seo_data)
        
        saved_file = None
        if save_post:
            # Save the post to files
            saved_file = save_blog_post(blog_post, keyword, "generated_posts")
            logger.info(f"Blog post saved to: {saved_file}")
        
        response = {
            "keyword": keyword,
            "seo_data": seo_data,
            "blog_post": blog_post,
            "generated_at": datetime.now().isoformat(),
            "saved_file": saved_file
        }
        
        return jsonify(response)
    
    except Exception as e:
        logger.error(f"Error generating blog post: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/posts')
def list_posts():
    """List all generated posts"""
    try:
        posts_dir = "generated_posts"
        daily_posts_dir = "daily_posts"
        
        posts = []
        
        # Check generated_posts directory
        if os.path.exists(posts_dir):
            for filename in os.listdir(posts_dir):
                if filename.endswith('.html'):
                    file_path = os.path.join(posts_dir, filename)
                    file_stat = os.stat(file_path)
                    posts.append({
                        "filename": filename,
                        "directory": "generated_posts",
                        "created": datetime.fromtimestamp(file_stat.st_ctime).isoformat(),
                        "size": file_stat.st_size,
                        "url": f"/posts/{filename}"
                    })
        
        # Check daily_posts directory
        if os.path.exists(daily_posts_dir):
            for filename in os.listdir(daily_posts_dir):
                if filename.endswith('.html'):
                    file_path = os.path.join(daily_posts_dir, filename)
                    file_stat = os.stat(file_path)
                    posts.append({
                        "filename": filename,
                        "directory": "daily_posts",
                        "created": datetime.fromtimestamp(file_stat.st_ctime).isoformat(),
                        "size": file_stat.st_size,
                        "url": f"/posts/{filename}?dir=daily"
                    })
        
        # Sort by creation time (newest first)
        posts.sort(key=lambda x: x['created'], reverse=True)
        
        return jsonify({
            "total_posts": len(posts),
            "posts": posts
        })
    
    except Exception as e:
        logger.error(f"Error listing posts: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/posts/<filename>')
def view_post(filename):
    """View a specific post"""
    try:
        post_dir = request.args.get('dir', 'generated')
        
        if post_dir == 'daily':
            file_path = os.path.join("daily_posts", filename)
        else:
            file_path = os.path.join("generated_posts", filename)
        
        if not os.path.exists(file_path):
            return jsonify({"error": "Post not found"}), 404
        
        return send_file(file_path, mimetype='text/html')
    
    except Exception as e:
        logger.error(f"Error viewing post: {str(e)}")
        return jsonify({"error": str(e)}), 500

def generate_daily_post():
    """Function to generate daily blog post for predefined keyword"""
    daily_keyword = os.getenv('DAILY_KEYWORD', 'wireless earbuds')
    
    try:
        logger.info(f"Starting daily blog post generation for: {daily_keyword}")
        
        # Get SEO data
        seo_data = get_seo_data(daily_keyword)
        
        # Generate blog post
        blog_post = generate_blog_post(daily_keyword, seo_data)
        
        # Save to daily_posts directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_keyword = daily_keyword.replace(' ', '_').replace('/', '_')
        
        # Create directory if it doesn't exist
        os.makedirs('daily_posts', exist_ok=True)
        
        # Save JSON data
        json_filename = f"daily_posts/daily_post_{safe_keyword}_{timestamp}.json"
        data = {
            "keyword": daily_keyword,
            "seo_data": seo_data,
            "blog_post": blog_post,
            "generated_at": datetime.now().isoformat()
        }
        
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Save HTML file
        html_filename = f"daily_posts/daily_post_{safe_keyword}_{timestamp}.html"
        with open(html_filename, 'w', encoding='utf-8') as f:
            f.write(blog_post['content'])
        
        logger.info(f"Daily blog post saved to: {html_filename}")
        
    except Exception as e:
        logger.error(f"Error in daily blog post generation: {str(e)}")

# Schedule daily blog post generation at 9 AM
scheduler.add_job(
    func=generate_daily_post,
    trigger=CronTrigger(hour=9, minute=00),  # 9:00 AM daily
    id='daily_blog_post',
    name='Generate Daily Blog Post',
    replace_existing=True
)

# For testing purposes, added a manual trigger endpoint
@app.route('/generate-daily', methods=['POST'])
def trigger_daily_generation():
    """Manually trigger daily post generation"""
    try:
        generate_daily_post()
        return jsonify({"message": "Daily post generation triggered successfully"})
    except Exception as e:
        logger.error(f"Error in manual daily generation: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/scheduler/status')
def scheduler_status():
    """Check scheduler status and jobs"""
    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({
            "id": job.id,
            "name": job.name,
            "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
            "trigger": str(job.trigger)
        })
    
    return jsonify({
        "scheduler_running": scheduler.running,
        "jobs": jobs
    })

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('generated_posts', exist_ok=True)
    os.makedirs('daily_posts', exist_ok=True)
    
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)