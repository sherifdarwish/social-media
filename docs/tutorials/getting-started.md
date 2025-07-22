# Getting Started with Social Media Agent

This comprehensive tutorial will guide you through setting up and using the Social Media Agent system, from initial installation to creating your first automated social media posts.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [First Steps](#first-steps)
5. [Creating Your First Post](#creating-your-first-post)
6. [Setting Up Automation](#setting-up-automation)
7. [Monitoring and Reports](#monitoring-and-reports)
8. [Advanced Features](#advanced-features)
9. [Troubleshooting](#troubleshooting)
10. [Next Steps](#next-steps)

## Prerequisites

Before you begin, ensure you have the following:

### System Requirements
- **Operating System**: Windows 10+, macOS 10.15+, or Linux (Ubuntu 18.04+)
- **Python**: Version 3.9 or higher
- **Memory**: At least 4GB RAM (8GB recommended)
- **Storage**: 10GB free space
- **Internet**: Stable broadband connection

### Required Accounts and API Keys

You'll need accounts and API access for:

1. **AI/LLM Providers** (at least one):
   - [OpenAI](https://platform.openai.com/) - For GPT and DALL-E
   - [Anthropic](https://console.anthropic.com/) - For Claude (optional)
   - [Google AI](https://ai.google.dev/) - For Gemini (optional)

2. **Social Media Platforms** (choose which ones you want to automate):
   - [Facebook Developer](https://developers.facebook.com/)
   - [Twitter Developer](https://developer.twitter.com/)
   - [Instagram Business](https://business.instagram.com/)
   - [LinkedIn Developer](https://developer.linkedin.com/)
   - [TikTok Developer](https://developers.tiktok.com/)

### Getting API Keys

#### OpenAI API Key
1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in to your account
3. Navigate to "API Keys" in your dashboard
4. Click "Create new secret key"
5. Copy and save the key securely

#### Facebook/Instagram API Setup
1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Create a new app or use an existing one
3. Add "Instagram Basic Display" and "Facebook Login" products
4. Generate access tokens for your pages/accounts
5. Note down App ID, App Secret, and Access Tokens

#### Twitter API Setup
1. Apply for a [Twitter Developer Account](https://developer.twitter.com/)
2. Create a new project and app
3. Generate API keys and tokens
4. Enable OAuth 2.0 and set permissions
5. Save API Key, API Secret, Bearer Token, Access Token, and Access Token Secret

## Installation

### Option 1: Quick Install (Recommended for Beginners)

```bash
# Install using pip (when available)
pip install social-media-agent
```

### Option 2: From Source (Recommended for Developers)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-org/social-media-agent.git
   cd social-media-agent
   ```

2. **Create a virtual environment**:
   ```bash
   # On Windows
   python -m venv venv
   venv\Scripts\activate

   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify installation**:
   ```bash
   python -c "import src; print('Installation successful!')"
   ```

### Option 3: Docker (Recommended for Production)

```bash
# Pull the official image
docker pull socialmediaagent/social-media-agent:latest

# Or build from source
git clone https://github.com/your-org/social-media-agent.git
cd social-media-agent
docker build -t social-media-agent:latest .
```

## Configuration

### Step 1: Create Configuration Files

1. **Copy the example configuration**:
   ```bash
   cp examples/config.example.yaml config/config.yaml
   ```

2. **Create environment file**:
   ```bash
   cp .env.example .env
   ```

### Step 2: Basic Configuration

Edit `config/config.yaml`:

```yaml
# Basic configuration for getting started
general:
  app_name: "My Social Media Agent"
  environment: "development"
  debug: true
  timezone: "UTC"

# Configure your LLM provider
llm_providers:
  openai:
    api_key: "${OPENAI_API_KEY}"
    api_base: "https://api.openai.com/v1"
    models:
      text: "gpt-4"
      image: "dall-e-3"
    rate_limits:
      requests_per_minute: 60
      tokens_per_minute: 90000

# Configure platforms you want to use
platforms:
  facebook:
    enabled: true
    api_credentials:
      access_token: "${FACEBOOK_ACCESS_TOKEN}"
      app_id: "${FACEBOOK_APP_ID}"
      app_secret: "${FACEBOOK_APP_SECRET}"
    posting_schedule:
      frequency: "daily"
      times: ["09:00", "15:00", "21:00"]
    content_settings:
      max_posts_per_day: 3
      content_types: ["text", "image"]

  twitter:
    enabled: true
    api_credentials:
      api_key: "${TWITTER_API_KEY}"
      api_secret: "${TWITTER_API_SECRET}"
      access_token: "${TWITTER_ACCESS_TOKEN}"
      access_token_secret: "${TWITTER_ACCESS_TOKEN_SECRET}"
    posting_schedule:
      frequency: "daily"
      times: ["08:00", "12:00", "18:00"]

# Content generation settings
content_generation:
  brand_voice:
    tone: "professional"
    personality: "helpful"
    style_guidelines:
      - "Use active voice"
      - "Keep sentences concise"
      - "Include relevant hashtags"
      - "Maintain consistent brand messaging"

  content_types:
    text:
      enabled: true
      max_length: 2000
      templates:
        - "tip"
        - "question"
        - "announcement"
        - "behind_the_scenes"
    
    image:
      enabled: true
      dimensions: "1080x1080"
      styles: ["professional", "modern", "colorful"]

# Team leader settings
team_leader:
  report_schedule: "weekly"
  report_day: "monday"
  report_time: "09:00"
  report_formats: ["html", "pdf"]
```

### Step 3: Environment Variables

Edit `.env` file:

```bash
# LLM Provider API Keys
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Facebook/Instagram
FACEBOOK_ACCESS_TOKEN=your_facebook_access_token
FACEBOOK_APP_ID=your_facebook_app_id
FACEBOOK_APP_SECRET=your_facebook_app_secret

# Twitter/X
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_ACCESS_TOKEN=your_twitter_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_twitter_access_token_secret

# LinkedIn
LINKEDIN_CLIENT_ID=your_linkedin_client_id
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret
LINKEDIN_ACCESS_TOKEN=your_linkedin_access_token

# Database (for development, SQLite is fine)
DATABASE_URL=sqlite:///./data/social_media_agent.db

# Redis (optional, for caching)
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your_secret_key_for_encryption
```

### Step 4: Initialize the Database

```bash
# Create necessary directories
mkdir -p data logs reports

# Initialize the database
python scripts/init_database.py
```

## First Steps

### Step 1: Verify Configuration

```bash
# Test configuration
python -c "
from src.config.config_manager import ConfigManager
config = ConfigManager('config/config.yaml')
errors = config.validate_config()
if errors:
    print('Configuration errors:', errors)
else:
    print('Configuration is valid!')
"
```

### Step 2: Test API Connections

```bash
# Test LLM provider connection
python scripts/test_connections.py --provider openai

# Test social media platform connections
python scripts/test_connections.py --platform facebook
python scripts/test_connections.py --platform twitter
```

### Step 3: Start the System

```python
# test_basic_functionality.py
import asyncio
from src.main import SocialMediaAgent

async def test_system():
    # Initialize the agent
    agent = SocialMediaAgent("config/config.yaml")
    
    # Check system status
    status = agent.get_system_status()
    print("System Status:", status)
    
    # Start all agents
    print("Starting agents...")
    success = await agent.start_all_agents()
    
    if success:
        print("✅ All agents started successfully!")
        
        # Check agent health
        health = await agent.health_check()
        print("Health Check:", health)
        
        # Stop agents
        await agent.stop_all_agents()
        print("✅ All agents stopped successfully!")
    else:
        print("❌ Failed to start some agents")

if __name__ == "__main__":
    asyncio.run(test_system())
```

Run the test:
```bash
python test_basic_functionality.py
```

## Creating Your First Post

### Step 1: Simple Text Post

```python
# create_first_post.py
import asyncio
from src.main import SocialMediaAgent

async def create_first_post():
    # Initialize and start the agent
    agent = SocialMediaAgent("config/config.yaml")
    await agent.start_all_agents()
    
    try:
        # Create a simple post
        result = await agent.create_coordinated_post(
            content_brief="Share a motivational quote about productivity",
            platforms=["facebook", "twitter"],  # Start with just these platforms
            content_type="text"
        )
        
        # Check results
        print("Post Results:")
        for platform, post_result in result.items():
            if post_result.success:
                print(f"✅ {platform.title()}: Posted successfully!")
                print(f"   Post ID: {post_result.post_id}")
                print(f"   URL: {post_result.url}")
                print(f"   Content: {post_result.content[:100]}...")
            else:
                print(f"❌ {platform.title()}: Failed to post")
                print(f"   Error: {post_result.error_message}")
            print()
    
    finally:
        # Always stop the agents
        await agent.stop_all_agents()

if __name__ == "__main__":
    asyncio.run(create_first_post())
```

### Step 2: Post with Image

```python
# create_post_with_image.py
import asyncio
from src.main import SocialMediaAgent

async def create_post_with_image():
    agent = SocialMediaAgent("config/config.yaml")
    await agent.start_all_agents()
    
    try:
        # Create a post with an AI-generated image
        result = await agent.create_coordinated_post(
            content_brief="Share tips about remote work productivity with a professional image",
            platforms=["facebook", "instagram"],
            content_type="image",
            image_style="professional",
            image_prompt="A clean, modern home office setup with a laptop, notebook, and coffee cup"
        )
        
        # Display results
        for platform, post_result in result.items():
            print(f"{platform.title()}: {'✅ Success' if post_result.success else '❌ Failed'}")
            if post_result.success:
                print(f"  Content: {post_result.content}")
                print(f"  URL: {post_result.url}")
    
    finally:
        await agent.stop_all_agents()

if __name__ == "__main__":
    asyncio.run(create_post_with_image())
```

### Step 3: Platform-Specific Posts

```python
# platform_specific_posts.py
import asyncio
from src.main import SocialMediaAgent

async def create_platform_specific_posts():
    agent = SocialMediaAgent("config/config.yaml")
    await agent.start_all_agents()
    
    try:
        # LinkedIn professional post
        linkedin_result = await agent.create_coordinated_post(
            content_brief="Share insights about digital transformation in business",
            platforms=["linkedin"],
            content_type="text",
            tone="professional",
            target_audience="business_professionals"
        )
        
        # Twitter thread
        twitter_result = await agent.create_coordinated_post(
            content_brief="Create a thread about productivity hacks for developers",
            platforms=["twitter"],
            content_type="thread",
            max_parts=5
        )
        
        # Instagram visual post
        instagram_result = await agent.create_coordinated_post(
            content_brief="Showcase our company culture with a behind-the-scenes image",
            platforms=["instagram"],
            content_type="image",
            image_style="casual",
            include_story=True
        )
        
        # Print results
        all_results = {
            "LinkedIn": linkedin_result.get("linkedin"),
            "Twitter": twitter_result.get("twitter"),
            "Instagram": instagram_result.get("instagram")
        }
        
        for platform, result in all_results.items():
            if result and result.success:
                print(f"✅ {platform}: {result.post_id}")
            else:
                print(f"❌ {platform}: Failed")
    
    finally:
        await agent.stop_all_agents()

if __name__ == "__main__":
    asyncio.run(create_platform_specific_posts())
```

## Setting Up Automation

### Step 1: Configure Posting Schedule

Edit your `config/config.yaml` to set up automated posting:

```yaml
automation:
  enabled: true
  posting_schedule:
    facebook:
      frequency: "daily"
      times: ["09:00", "15:00", "21:00"]
      content_types: ["text", "image"]
    
    twitter:
      frequency: "daily"
      times: ["08:00", "12:00", "16:00", "20:00"]
      content_types: ["text", "thread"]
    
    linkedin:
      frequency: "daily"
      times: ["07:00", "17:00"]
      content_types: ["text", "article"]
    
    instagram:
      frequency: "daily"
      times: ["10:00", "18:00"]
      content_types: ["image"]

content_strategy:
  themes:
    monday: "motivation"
    tuesday: "tips_and_tricks"
    wednesday: "behind_the_scenes"
    thursday: "industry_insights"
    friday: "fun_facts"
    saturday: "user_generated_content"
    sunday: "inspiration"
  
  content_mix:
    educational: 40%
    promotional: 20%
    entertaining: 25%
    inspirational: 15%
```

### Step 2: Start Automated Mode

```python
# start_automation.py
import asyncio
from src.main import SocialMediaAgent

async def start_automation():
    agent = SocialMediaAgent("config/config.yaml")
    
    # Start all agents
    await agent.start_all_agents()
    
    print("🤖 Social Media Agent is now running in automated mode!")
    print("📅 Posts will be created according to your schedule")
    print("📊 Weekly reports will be generated automatically")
    print("🔍 Monitor the logs for activity updates")
    
    try:
        # Keep the system running
        while True:
            # Check system health every hour
            health = await agent.health_check()
            if not all(h.get("healthy", False) for h in health.values()):
                print("⚠️  Some agents are unhealthy:", health)
            
            # Wait for an hour before next check
            await asyncio.sleep(3600)
    
    except KeyboardInterrupt:
        print("\n🛑 Stopping automation...")
        await agent.stop_all_agents()
        print("✅ Automation stopped successfully")

if __name__ == "__main__":
    asyncio.run(start_automation())
```

### Step 3: Running as a Service

#### Option 1: Using systemd (Linux)

Create `/etc/systemd/system/social-media-agent.service`:

```ini
[Unit]
Description=Social Media Agent
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/social-media-agent
Environment=PATH=/path/to/social-media-agent/venv/bin
ExecStart=/path/to/social-media-agent/venv/bin/python start_automation.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl enable social-media-agent
sudo systemctl start social-media-agent
sudo systemctl status social-media-agent
```

#### Option 2: Using Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  social-media-agent:
    build: .
    restart: unless-stopped
    volumes:
      - ./config:/app/config
      - ./data:/app/data
      - ./logs:/app/logs
    environment:
      - ENVIRONMENT=production
    env_file:
      - .env
    depends_on:
      - redis
      - db

  redis:
    image: redis:7-alpine
    restart: unless-stopped

  db:
    image: postgres:15
    restart: unless-stopped
    environment:
      POSTGRES_DB: social_media_agent
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

Start with Docker Compose:
```bash
docker-compose up -d
```

## Monitoring and Reports

### Step 1: Check System Status

```python
# check_status.py
import asyncio
from src.main import SocialMediaAgent

async def check_status():
    agent = SocialMediaAgent("config/config.yaml")
    
    # Get system status
    status = agent.get_system_status()
    print("📊 System Status:")
    print(f"  Uptime: {status.get('uptime', 'Unknown')}")
    print(f"  Active Agents: {len(status.get('active_agents', []))}")
    print(f"  Total Posts Today: {status.get('posts_today', 0)}")
    print()
    
    # Check agent health
    health = await agent.health_check()
    print("🏥 Agent Health:")
    for agent_name, health_info in health.items():
        status_emoji = "✅" if health_info.get("healthy", False) else "❌"
        print(f"  {status_emoji} {agent_name}: {health_info.get('status', 'Unknown')}")
    print()
    
    # Get recent metrics
    # This would typically come from your metrics collector
    print("📈 Recent Metrics:")
    print("  Posts created today: 12")
    print("  Average engagement rate: 3.2%")
    print("  Success rate: 95%")

if __name__ == "__main__":
    asyncio.run(check_status())
```

### Step 2: Generate Reports

```python
# generate_report.py
import asyncio
from datetime import datetime, timedelta
from src.main import SocialMediaAgent

async def generate_weekly_report():
    agent = SocialMediaAgent("config/config.yaml")
    
    # Generate weekly report
    print("📊 Generating weekly report...")
    report = await agent.generate_weekly_report(
        start_date=datetime.now() - timedelta(days=7),
        end_date=datetime.now(),
        format="html"
    )
    
    print("✅ Weekly report generated!")
    print(f"📄 Report saved to: {report.get('file_path', 'reports/weekly_report.html')}")
    print()
    
    # Display summary
    summary = report.get("summary", {})
    print("📈 Weekly Summary:")
    print(f"  Total Posts: {summary.get('total_posts', 0)}")
    print(f"  Total Engagement: {summary.get('total_engagement', 0)}")
    print(f"  Average Engagement Rate: {summary.get('avg_engagement_rate', 0):.2f}%")
    print(f"  Top Performing Platform: {summary.get('top_platform', 'N/A')}")
    print()
    
    # Show recommendations
    recommendations = report.get("recommendations", [])
    if recommendations:
        print("💡 Recommendations:")
        for i, rec in enumerate(recommendations[:3], 1):
            print(f"  {i}. {rec}")

if __name__ == "__main__":
    asyncio.run(generate_weekly_report())
```

### Step 3: Set Up Monitoring Dashboard

Create a simple web dashboard:

```python
# dashboard.py
from flask import Flask, render_template, jsonify
from src.main import SocialMediaAgent
import asyncio

app = Flask(__name__)
agent = SocialMediaAgent("config/config.yaml")

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/status')
def api_status():
    status = agent.get_system_status()
    return jsonify(status)

@app.route('/api/health')
async def api_health():
    health = await agent.health_check()
    return jsonify(health)

@app.route('/api/metrics')
def api_metrics():
    # Return recent metrics
    metrics = {
        "posts_today": 12,
        "engagement_rate": 3.2,
        "success_rate": 95.0,
        "active_agents": 5
    }
    return jsonify(metrics)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

## Advanced Features

### Custom Content Templates

Create custom content templates for different types of posts:

```python
# custom_templates.py
from src.content_generation.content_generator import ContentGenerator

class CustomContentGenerator(ContentGenerator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.custom_templates = {
            "product_launch": {
                "facebook": "🚀 Exciting news! We're launching {product_name}! {description} What do you think? #ProductLaunch #Innovation",
                "twitter": "🚀 Big announcement: {product_name} is here! {description} Thread below 👇 #ProductLaunch",
                "linkedin": "I'm excited to announce the launch of {product_name}. {description} This represents a significant step forward in our mission to {mission}."
            },
            "tip_tuesday": {
                "facebook": "💡 Tip Tuesday: {tip_content} Have you tried this? Let us know in the comments! #TipTuesday #Productivity",
                "twitter": "💡 #TipTuesday: {tip_content} What's your favorite productivity hack? 🧵",
                "linkedin": "Professional tip: {tip_content} In my experience, this approach has proven effective for {benefit}."
            }
        }
    
    async def generate_from_template(self, template_name, platform, **kwargs):
        template = self.custom_templates.get(template_name, {}).get(platform)
        if template:
            return template.format(**kwargs)
        else:
            # Fall back to AI generation
            return await super().generate_text_content(
                f"Create a {template_name} post for {platform}",
                platform
            )
```

### A/B Testing

Implement A/B testing for your content:

```python
# ab_testing.py
import asyncio
import random
from src.main import SocialMediaAgent

async def run_ab_test():
    agent = SocialMediaAgent("config/config.yaml")
    await agent.start_all_agents()
    
    try:
        # Define two versions of content
        version_a = "Boost your productivity with these 5 simple tips!"
        version_b = "Transform your workday: 5 game-changing productivity hacks"
        
        # Randomly assign version to different platforms
        platforms = ["facebook", "twitter", "linkedin"]
        random.shuffle(platforms)
        
        # Test version A on first half
        result_a = await agent.create_coordinated_post(
            content_brief=version_a,
            platforms=platforms[:len(platforms)//2],
            content_type="text"
        )
        
        # Test version B on second half
        result_b = await agent.create_coordinated_post(
            content_brief=version_b,
            platforms=platforms[len(platforms)//2:],
            content_type="text"
        )
        
        print("A/B Test Results:")
        print(f"Version A: {list(result_a.keys())}")
        print(f"Version B: {list(result_b.keys())}")
        
        # Store results for later analysis
        # You would typically save this to a database
        
    finally:
        await agent.stop_all_agents()

if __name__ == "__main__":
    asyncio.run(run_ab_test())
```

### Content Calendar Integration

Create a content calendar system:

```python
# content_calendar.py
import asyncio
from datetime import datetime, timedelta
from src.main import SocialMediaAgent

class ContentCalendar:
    def __init__(self, agent):
        self.agent = agent
        self.calendar = {}
    
    def schedule_post(self, date, time, content_brief, platforms, **kwargs):
        """Schedule a post for a specific date and time."""
        schedule_key = f"{date}_{time}"
        self.calendar[schedule_key] = {
            "content_brief": content_brief,
            "platforms": platforms,
            "kwargs": kwargs,
            "scheduled_for": datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        }
    
    def schedule_weekly_content(self):
        """Schedule a week's worth of content."""
        base_date = datetime.now().date()
        
        # Monday - Motivation
        self.schedule_post(
            base_date + timedelta(days=0), "09:00",
            "Share a motivational quote about starting the week strong",
            ["facebook", "twitter", "linkedin"]
        )
        
        # Tuesday - Tips
        self.schedule_post(
            base_date + timedelta(days=1), "10:00",
            "Share 3 productivity tips for remote workers",
            ["facebook", "linkedin"]
        )
        
        # Wednesday - Behind the scenes
        self.schedule_post(
            base_date + timedelta(days=2), "14:00",
            "Show behind-the-scenes of our team working on a project",
            ["instagram", "facebook"],
            content_type="image"
        )
        
        # Thursday - Industry insights
        self.schedule_post(
            base_date + timedelta(days=3), "11:00",
            "Share insights about the latest trends in our industry",
            ["linkedin", "twitter"]
        )
        
        # Friday - Fun content
        self.schedule_post(
            base_date + timedelta(days=4), "15:00",
            "Share a fun fact related to our industry",
            ["facebook", "twitter", "instagram"]
        )
    
    async def execute_scheduled_posts(self):
        """Execute posts that are scheduled for now."""
        now = datetime.now()
        
        for schedule_key, post_data in list(self.calendar.items()):
            scheduled_time = post_data["scheduled_for"]
            
            # Check if it's time to post (within 5 minutes)
            if abs((now - scheduled_time).total_seconds()) <= 300:
                print(f"⏰ Executing scheduled post: {post_data['content_brief']}")
                
                result = await self.agent.create_coordinated_post(
                    content_brief=post_data["content_brief"],
                    platforms=post_data["platforms"],
                    **post_data["kwargs"]
                )
                
                # Remove from calendar after execution
                del self.calendar[schedule_key]
                
                print(f"✅ Scheduled post executed for {post_data['platforms']}")

async def main():
    agent = SocialMediaAgent("config/config.yaml")
    calendar = ContentCalendar(agent)
    
    # Schedule a week's worth of content
    calendar.schedule_weekly_content()
    
    print(f"📅 Scheduled {len(calendar.calendar)} posts")
    
    # Start agents
    await agent.start_all_agents()
    
    try:
        # Run the scheduler (in production, this would run continuously)
        await calendar.execute_scheduled_posts()
    finally:
        await agent.stop_all_agents()

if __name__ == "__main__":
    asyncio.run(main())
```

## Troubleshooting

### Common Issues and Solutions

#### Issue 1: "Configuration Error"
```
Error: Configuration file not found or invalid
```

**Solution:**
```bash
# Check if config file exists
ls -la config/config.yaml

# Validate configuration
python -c "
from src.config.config_manager import ConfigManager
config = ConfigManager('config/config.yaml')
print(config.validate_config())
"

# Copy example if missing
cp examples/config.example.yaml config/config.yaml
```

#### Issue 2: "API Key Invalid"
```
Error: Invalid API key for provider 'openai'
```

**Solution:**
```bash
# Test API key directly
python -c "
import openai
openai.api_key = 'your-api-key'
try:
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[{'role': 'user', 'content': 'Hello'}],
        max_tokens=5
    )
    print('API key is valid')
except Exception as e:
    print(f'API key error: {e}')
"
```

#### Issue 3: "Rate Limit Exceeded"
```
Error: Rate limit exceeded for platform 'twitter'
```

**Solution:**
```python
# Implement rate limiting in your config
platforms:
  twitter:
    rate_limits:
      posts_per_hour: 50
      posts_per_day: 300
    retry_settings:
      max_retries: 3
      backoff_factor: 2
```

#### Issue 4: "Database Connection Failed"
```
Error: Could not connect to database
```

**Solution:**
```bash
# For SQLite (development)
mkdir -p data
python scripts/init_database.py

# For PostgreSQL (production)
# Check connection
psql $DATABASE_URL -c "SELECT 1;"

# Create database if needed
createdb social_media_agent
```

### Debug Mode

Enable debug mode for detailed logging:

```python
# debug_mode.py
import logging
from src.main import SocialMediaAgent

# Enable debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def debug_session():
    agent = SocialMediaAgent("config/config.yaml", log_level="DEBUG")
    
    # This will show detailed logs
    await agent.start_all_agents()
    
    # Test a simple operation
    result = await agent.create_coordinated_post(
        content_brief="Test post for debugging",
        platforms=["twitter"]
    )
    
    print("Debug result:", result)
    
    await agent.stop_all_agents()

if __name__ == "__main__":
    import asyncio
    asyncio.run(debug_session())
```

## Next Steps

Congratulations! You've successfully set up and used the Social Media Agent. Here are some next steps to explore:

### 1. Advanced Configuration
- Set up multiple brand voices for different audiences
- Configure advanced content strategies
- Implement custom content templates

### 2. Scaling Up
- Deploy to production using Docker or Kubernetes
- Set up monitoring and alerting
- Implement backup and disaster recovery

### 3. Customization
- Create custom platform agents
- Develop custom content generators
- Build custom reporting dashboards

### 4. Integration
- Integrate with your CRM system
- Connect to analytics platforms
- Set up webhook notifications

### 5. Community and Support
- Join our [Discord community](https://discord.gg/social-media-agent)
- Contribute to the project on [GitHub](https://github.com/your-org/social-media-agent)
- Read the [advanced documentation](../api/README.md)

### Useful Resources

- **API Documentation**: [docs/api/README.md](../api/README.md)
- **Deployment Guide**: [docs/deployment/README.md](../deployment/README.md)
- **Configuration Reference**: [examples/config.example.yaml](../../examples/config.example.yaml)
- **Example Scripts**: [examples/](../../examples/)
- **GitHub Issues**: [Report bugs and request features](https://github.com/your-org/social-media-agent/issues)

Happy automating! 🚀

