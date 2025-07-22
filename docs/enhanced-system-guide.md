# Enhanced Social Media Agent System Guide

## Overview

The Enhanced Social Media Agent System is an advanced version of the original social media automation platform that includes two new powerful agents:

1. **Generator Agent** - Handles content briefing and intelligent content suggestions
2. **Evaluation Agent** - Processes user feedback and drives continuous improvement

This enhanced system provides a complete content approval workflow with machine learning-driven optimization.

## Table of Contents

1. [System Architecture](#system-architecture)
2. [New Components](#new-components)
3. [Content Approval Workflow](#content-approval-workflow)
4. [Installation and Setup](#installation-and-setup)
5. [Configuration](#configuration)
6. [Usage Guide](#usage-guide)
7. [API Reference](#api-reference)
8. [Troubleshooting](#troubleshooting)

## System Architecture

### Enhanced Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                Enhanced Team Leader Agent                   │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │  Generator      │  │  Evaluation     │  │  Platform   │ │
│  │  Agent          │  │  Agent          │  │  Agents     │ │
│  │                 │  │                 │  │  (5 agents) │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              Content Approval Interface                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │  Content Cards  │  │  Feedback       │  │  Analytics  │ │
│  │  Display        │  │  Collection     │  │  Dashboard  │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Component Relationships

- **Enhanced Team Leader**: Orchestrates the entire workflow including approval processes
- **Generator Agent**: Creates business briefings and generates content suggestions
- **Evaluation Agent**: Analyzes feedback and provides optimization recommendations
- **Content Approval Interface**: Web-based UI for reviewing and approving content
- **Platform Agents**: Handle posting to specific social media platforms

## New Components

### Generator Agent

The Generator Agent is responsible for:

- **Business Analysis**: Understanding your business domain, target audience, and objectives
- **Content Strategy**: Developing platform-specific content strategies
- **Content Generation**: Creating multiple content suggestions based on briefings
- **Optimization**: Ensuring content is optimized for each platform

#### Key Features:
- Configurable number of content suggestions (1-50 posts)
- Multi-platform optimization
- Industry-specific content strategies
- Hashtag research and optimization
- Optimal timing suggestions

### Evaluation Agent

The Evaluation Agent provides:

- **Feedback Analysis**: Processing user approval/rejection decisions
- **Pattern Recognition**: Identifying what content performs well
- **Machine Learning**: Continuously improving content recommendations
- **Performance Tracking**: Monitoring content effectiveness

#### Key Features:
- Real-time feedback processing
- Sentiment analysis of user comments
- Predictive content scoring
- Automated optimization recommendations
- Performance trend analysis

### Content Approval Interface

A web-based interface that provides:

- **Content Cards**: Visual display of generated content suggestions
- **Approval Controls**: Approve, reject, thumbs up/down options
- **Feedback Collection**: Comment and rating system
- **Real-time Updates**: Live status updates and notifications

## Content Approval Workflow

### Step-by-Step Process

1. **Business Briefing Creation**
   ```
   User provides business information → Generator Agent analyzes → Creates briefing
   ```

2. **Content Generation**
   ```
   Briefing → Content strategy → Multiple content suggestions → Platform optimization
   ```

3. **Content Presentation**
   ```
   Suggestions displayed in approval interface → User reviews content cards
   ```

4. **Approval Process**
   ```
   User provides feedback → Approve/Reject/Rate content → Comments collected
   ```

5. **Feedback Analysis**
   ```
   Evaluation Agent processes feedback → Identifies patterns → Updates ML model
   ```

6. **Content Scheduling**
   ```
   Approved content → Optimal timing calculation → Platform-specific posting
   ```

7. **Performance Monitoring**
   ```
   Posted content tracked → Engagement metrics collected → Feedback loop closed
   ```

### Approval Options

- **Approve** ✅: Content is approved for posting
- **Reject** ❌: Content is rejected and won't be posted
- **Thumbs Up** 👍: Positive feedback for learning
- **Thumbs Down** 👎: Negative feedback for improvement
- **Comments**: Detailed feedback for specific improvements

## Installation and Setup

### Prerequisites

- Python 3.8 or higher
- Node.js 14 or higher (for the approval interface)
- Required API keys for social media platforms
- LLM API keys (OpenAI, Anthropic, etc.)

### Installation Steps

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-org/social-media-agent.git
   cd social-media-agent
   ```

2. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # For development
   ```

3. **Set Up the Approval Interface**
   ```bash
   cd content-approval-interface
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

5. **Initialize Database**
   ```bash
   python scripts/init_database.py
   ```

### Quick Start

1. **Start the Enhanced System**
   ```bash
   python src/main_enhanced.py --config examples/config.enhanced.yaml
   ```

2. **Start the Approval Interface**
   ```bash
   cd content-approval-interface
   python src/main.py
   ```

3. **Access the Interface**
   Open your browser to `http://localhost:5000`

## Configuration

### Enhanced Configuration File

The enhanced system uses an extended configuration file. Key new sections:

```yaml
# Generator Agent Configuration
generator_agent:
  enabled: true
  content_generation:
    default_count: 10
    max_count: 50
  llm_providers:
    primary: "openai"
    fallback: ["anthropic", "google"]

# Evaluation Agent Configuration
evaluation_agent:
  enabled: true
  machine_learning:
    model_update_frequency: "daily"
    min_training_samples: 20
    learning_rate: 0.1

# Workflow Configuration
workflow:
  approval_required: true
  auto_post_threshold: 0.8
  approval_timeout: 24  # hours
```

### Environment Variables

```bash
# LLM API Keys
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
GOOGLE_AI_API_KEY=your_google_key

# Social Media API Keys
FACEBOOK_ACCESS_TOKEN=your_facebook_token
TWITTER_API_KEY=your_twitter_key
INSTAGRAM_ACCESS_TOKEN=your_instagram_token
LINKEDIN_ACCESS_TOKEN=your_linkedin_token
TIKTOK_ACCESS_TOKEN=your_tiktok_token

# Database Configuration
DATABASE_URL=sqlite:///data/enhanced_agent.db
```

## Usage Guide

### Creating a Content Campaign

1. **Prepare Business Information**
   ```python
   business_info = {
       'name': 'Your Business Name',
       'industry': 'Your Industry',
       'target_audience': 'Your Target Audience',
       'brand_voice': 'Your Brand Voice',
       'products_services': ['Service 1', 'Service 2'],
       'goals': ['Goal 1', 'Goal 2']
   }
   ```

2. **Create Campaign Request**
   ```python
   campaign_request = {
       'name': 'Q1 Marketing Campaign',
       'business_info': business_info,
       'platforms': ['facebook', 'twitter', 'instagram'],
       'content_count': 15,
       'content_types': ['educational', 'promotional', 'entertaining'],
       'objectives': ['engagement', 'brand_awareness', 'lead_generation']
   }
   ```

3. **Submit Campaign**
   ```python
   result = await system.create_content_campaign(campaign_request)
   ```

### Using the Approval Interface

1. **Access the Interface**
   - Navigate to `http://localhost:5000`
   - Log in with your credentials

2. **Review Content Cards**
   - Each card shows a content suggestion
   - Preview how it will look on each platform
   - See engagement predictions and optimal timing

3. **Provide Feedback**
   - Click approve/reject buttons
   - Use thumbs up/down for quick feedback
   - Add detailed comments for specific improvements

4. **Monitor Progress**
   - Track approval status in real-time
   - View scheduled posting times
   - Monitor posting results

### API Usage

#### Create Content Campaign
```python
import asyncio
from main_enhanced import EnhancedSocialMediaAgentSystem

async def create_campaign():
    system = EnhancedSocialMediaAgentSystem()
    await system.start()
    
    campaign_request = {
        'name': 'Test Campaign',
        'business_info': {
            'name': 'Test Business',
            'industry': 'Technology'
        },
        'platforms': ['facebook', 'twitter'],
        'content_count': 5
    }
    
    result = await system.create_content_campaign(campaign_request)
    print(f"Campaign created: {result}")
    
    await system.stop()

asyncio.run(create_campaign())
```

#### Process Approvals
```python
async def process_approvals():
    system = EnhancedSocialMediaAgentSystem()
    await system.start()
    
    approval_data = {
        'campaign_id': 'your_campaign_id',
        'approvals': {
            'suggestion_1': {
                'action': 'approve',
                'comments': 'Great content!'
            },
            'suggestion_2': {
                'action': 'reject',
                'comments': 'Needs more engaging hook'
            }
        }
    }
    
    result = await system.process_content_approval(approval_data)
    print(f"Approvals processed: {result}")
    
    await system.stop()

asyncio.run(process_approvals())
```

### Getting Recommendations

```python
async def get_recommendations():
    system = EnhancedSocialMediaAgentSystem()
    await system.start()
    
    request_data = {
        'platform': 'facebook',
        'content_type': 'educational',
        'current_content': {
            'text': 'Your current content text',
            'hashtags': ['#current', '#hashtags']
        }
    }
    
    recommendations = await system.get_content_recommendations(request_data)
    print(f"Recommendations: {recommendations}")
    
    await system.stop()

asyncio.run(get_recommendations())
```

## API Reference

### Enhanced Team Leader API

#### `create_content_campaign(campaign_request)`
Creates a new content campaign with generated suggestions.

**Parameters:**
- `campaign_request` (dict): Campaign configuration and requirements

**Returns:**
- `dict`: Campaign creation result with content suggestions

#### `process_content_approval(approval_data)`
Processes user approval decisions for content suggestions.

**Parameters:**
- `approval_data` (dict): Approval decisions and feedback

**Returns:**
- `dict`: Processing result and next steps

#### `get_content_recommendations(request_data)`
Gets content improvement recommendations from the evaluation agent.

**Parameters:**
- `request_data` (dict): Request parameters for recommendations

**Returns:**
- `dict`: Content recommendations and optimization suggestions

### Generator Agent API

#### `create_business_briefing(business_info)`
Creates a comprehensive business briefing for content generation.

**Parameters:**
- `business_info` (dict): Business information and context

**Returns:**
- `dict`: Business briefing with analysis and strategy

#### `generate_content_suggestions(content_request)`
Generates multiple content suggestions based on briefing.

**Parameters:**
- `content_request` (dict): Content generation parameters

**Returns:**
- `dict`: List of content suggestions with metadata

### Evaluation Agent API

#### `process_feedback(feedback_data)`
Processes user feedback for machine learning improvement.

**Parameters:**
- `feedback_data` (dict): Feedback information and context

**Returns:**
- `dict`: Feedback analysis result

#### `analyze_feedback_patterns(analysis_request)`
Analyzes feedback patterns to identify trends and insights.

**Parameters:**
- `analysis_request` (dict): Analysis parameters and time range

**Returns:**
- `dict`: Pattern analysis results and metrics

## Troubleshooting

### Common Issues

#### 1. System Won't Start
**Problem**: Enhanced system fails to start
**Solutions:**
- Check API key configuration
- Verify database connectivity
- Review log files for specific errors
- Ensure all dependencies are installed

#### 2. Content Generation Fails
**Problem**: Generator Agent can't create content
**Solutions:**
- Verify LLM API keys are valid
- Check API rate limits
- Review business briefing data
- Test with simpler content requests

#### 3. Approval Interface Not Loading
**Problem**: Web interface is inaccessible
**Solutions:**
- Check if Flask app is running
- Verify port 5000 is available
- Review browser console for errors
- Check CORS configuration

#### 4. Feedback Not Processing
**Problem**: Evaluation Agent not processing feedback
**Solutions:**
- Check database connectivity
- Verify feedback data format
- Review evaluation agent logs
- Ensure minimum training samples are met

### Debug Mode

Enable debug mode for detailed logging:

```bash
python src/main_enhanced.py --debug --config examples/config.enhanced.yaml
```

### Log Files

Check log files for detailed error information:
- `logs/enhanced_system.log` - Main system logs
- `logs/generator_agent.log` - Generator Agent logs
- `logs/evaluation_agent.log` - Evaluation Agent logs
- `logs/approval_interface.log` - Web interface logs

### Performance Monitoring

Monitor system performance:

```python
# Get system status
status = await system.get_system_status()
print(f"System Status: {status}")

# Generate performance report
report = await system.generate_performance_report('daily')
print(f"Performance Report: {report}")
```

### Support

For additional support:
1. Check the [GitHub Issues](https://github.com/your-org/social-media-agent/issues)
2. Review the [API Documentation](docs/api/README.md)
3. Consult the [Deployment Guide](docs/deployment/README.md)
4. Contact the development team

## Best Practices

### Content Generation
- Provide detailed business information for better briefings
- Use specific, measurable objectives
- Test with small content counts initially
- Review and refine based on feedback

### Approval Workflow
- Provide detailed feedback comments
- Use consistent approval criteria
- Review content regularly to maintain quality
- Monitor approval rates and adjust thresholds

### Performance Optimization
- Monitor system metrics regularly
- Adjust ML parameters based on performance
- Use auto-approval for high-confidence content
- Implement proper error handling and recovery

### Security
- Regularly rotate API keys
- Use environment variables for sensitive data
- Implement proper access controls
- Monitor for unusual activity

## Conclusion

The Enhanced Social Media Agent System provides a powerful, intelligent platform for automated social media content creation and management. With the addition of the Generator and Evaluation agents, along with the content approval workflow, you can ensure high-quality, engaging content that continuously improves based on user feedback and performance data.

The system is designed to scale with your needs and can be customized for various business types and social media strategies. Regular monitoring and optimization will help you achieve the best results from your social media automation efforts.

