# Requirements.txt

```
Flask==3.0.0
openai==1.3.0
python-dotenv==1.0.0
APScheduler==3.10.4
```

# README.md

````markdown

An automated blog post generation system that uses SEO data and OpenAI to create affiliate marketing content with daily scheduling capabilities.

## Features

- SEO keyword research with search volume, difficulty, and CPC data
- AI-powered blog post generation using OpenAI GPT
- Automatic affiliate link insertion
- Daily scheduled post generation
- REST API for manual generation
- HTML output with proper structure and styling
- Fallback content generation

## Setup Instructions

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/ai-blog-generator-interview-[YourName]
cd ai-blog-generator-interview-[YourName]
```
````

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Configuration

Create a `.env` file in the project root:

```bash
OPENAI_API_KEY=your_openai_api_key_here
DAILY_KEYWORD=your_chosen_keyword_here
DEBUG=False
```

### 4. Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

## API Endpoints

### Generate Blog Post

```
GET /generate?keyword=<keyword>&save=true
```

Generates a blog post for the specified keyword.

### List Generated Posts

```
GET /posts
```

Lists all generated blog posts.

### View Specific Post

```
GET /posts/<filename>
```

View a specific generated blog post.

### Manual Daily Generation

```
POST /generate-daily
```

Manually trigger daily post generation.

### Scheduler Status

```
GET /scheduler/status
```

Check scheduler status and upcoming jobs.

## Daily Scheduler

The application includes an APScheduler that automatically generates a blog post daily at 9:00 AM for the keyword specified in the `DAILY_KEYWORD` environment variable.

Generated posts are saved in the `daily_posts/` directory with timestamps.

## Example Usage

```bash
# Generate a blog post about wireless earbuds
curl "http://localhost:5000/generate?keyword=wireless%20earbuds&save=true"

# List all generated posts
curl "http://localhost:5000/posts"

# Manually trigger daily generation
curl -X POST "http://localhost:5000/generate-daily"
```

## File Structure

```
├── app.py                 # Main Flask application
├── ai_generator.py        # OpenAI blog post generation
├── seo_fetcher.py        # SEO data fetching (mock)
├── mock_seo_data.json    # Mock SEO database
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables
├── generated_posts/      # Manual generations
├── daily_posts/         # Daily scheduled posts
└── README.md            # This file
```

## Mock SEO Data

The application includes a random mock SEO database with realistic metrics for testing. In production, this could be replaced with real API calls to services like SEMrush, Ahrefs, or Google Keyword Planner.

## Generated Content Features

- SEO-optimized titles and meta descriptions
- Structured content with H2/H3 headings
- Natural keyword incorporation
- Placeholder affiliate links ({{AFF_LINK_1}}, etc.)
- FAQ sections
- Reading time estimation
- Word count tracking
- Proper HTML formatting

## Error Handling

The application includes error handling:

- Fallback content generation if OpenAI API fails
- Graceful handling of missing environment variables
- Comprehensive logging
- API error responses

## Customization

- Modify `DAILY_KEYWORD` in `.env` to change the daily generation keyword
- Update affiliate link templates in `ai_generator.py`
- Customize SEO data in `mock_seo_data.json`
- Adjust scheduler timing in `app.py`

```

# .env.example

```

OPENAI_API_KEY=your_openai_api_key_here
DAILY_KEYWORD=wireless earbuds
DEBUG=False
PORT=5000

```

```
