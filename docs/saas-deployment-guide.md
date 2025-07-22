# Social Media Agent SaaS Platform - Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying the Social Media Agent SaaS platform to production environments. The platform is designed to be cloud-native and supports deployment on major cloud providers.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Database Configuration](#database-configuration)
4. [Application Deployment](#application-deployment)
5. [Frontend Deployment](#frontend-deployment)
6. [SSL/TLS Configuration](#ssltls-configuration)
7. [Monitoring and Logging](#monitoring-and-logging)
8. [Backup and Recovery](#backup-and-recovery)
9. [Scaling and Performance](#scaling-and-performance)
10. [Security Considerations](#security-considerations)
11. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

- **Operating System**: Ubuntu 20.04+ or CentOS 8+
- **Memory**: Minimum 4GB RAM (8GB+ recommended for production)
- **Storage**: Minimum 50GB SSD (100GB+ recommended)
- **CPU**: Minimum 2 cores (4+ cores recommended)
- **Network**: Stable internet connection with public IP

### Required Services

- **Database**: PostgreSQL 13+ or MySQL 8+
- **Cache**: Redis 6+
- **Message Queue**: Redis or RabbitMQ
- **File Storage**: AWS S3 or compatible object storage
- **Email Service**: SMTP server or service (SendGrid, Mailgun, etc.)

### Third-Party Accounts

- **Stripe**: For payment processing
- **Social Media APIs**: Facebook, Twitter, LinkedIn, Instagram, TikTok
- **AI Services**: OpenAI, Anthropic, Google AI
- **Cloud Provider**: AWS, Google Cloud, or Azure

## Environment Setup

### 1. Server Preparation

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3.11 python3.11-venv python3-pip nginx postgresql-client redis-tools git curl

# Install Node.js (for frontend)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install Docker (optional, for containerized deployment)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

### 2. Application Setup

```bash
# Clone the repository
git clone https://github.com/your-org/social-media-agent.git
cd social-media-agent

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
pip install -r requirements-prod.txt

# Install frontend dependencies
cd saas-frontend
npm install
npm run build
cd ..
```

### 3. Environment Variables

Create a `.env` file in the project root:

```bash
# Application Settings
SECRET_KEY=your-super-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
ENVIRONMENT=production
DEBUG=false

# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/social_media_agent
REDIS_URL=redis://localhost:6379/0

# Stripe Configuration
STRIPE_PUBLISHABLE_KEY=pk_live_your_publishable_key
STRIPE_SECRET_KEY=sk_live_your_secret_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
STRIPE_FREE_PLAN_PRICE_ID=price_free_plan_id
STRIPE_PRO_PLAN_PRICE_ID=price_pro_plan_id

# Social Media OAuth
FACEBOOK_CLIENT_ID=your_facebook_client_id
FACEBOOK_CLIENT_SECRET=your_facebook_client_secret
FACEBOOK_REDIRECT_URI=https://yourdomain.com/api/v1/social/auth/facebook/callback

TWITTER_CLIENT_ID=your_twitter_client_id
TWITTER_CLIENT_SECRET=your_twitter_client_secret
TWITTER_REDIRECT_URI=https://yourdomain.com/api/v1/social/auth/twitter/callback

LINKEDIN_CLIENT_ID=your_linkedin_client_id
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret
LINKEDIN_REDIRECT_URI=https://yourdomain.com/api/v1/social/auth/linkedin/callback

INSTAGRAM_CLIENT_ID=your_instagram_client_id
INSTAGRAM_CLIENT_SECRET=your_instagram_client_secret
INSTAGRAM_REDIRECT_URI=https://yourdomain.com/api/v1/social/auth/instagram/callback

TIKTOK_CLIENT_ID=your_tiktok_client_id
TIKTOK_CLIENT_SECRET=your_tiktok_client_secret
TIKTOK_REDIRECT_URI=https://yourdomain.com/api/v1/social/auth/tiktok/callback

# AI Services
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
GOOGLE_AI_API_KEY=your_google_ai_api_key

# Email Configuration
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=your_sendgrid_api_key
FROM_EMAIL=noreply@yourdomain.com

# File Storage
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
S3_BUCKET_NAME=your-s3-bucket
AWS_REGION=us-east-1

# Security
SOCIAL_TOKEN_ENCRYPTION_KEY=your-32-byte-encryption-key
FRONTEND_URL=https://yourdomain.com

# Monitoring
SENTRY_DSN=your_sentry_dsn

# Background Jobs
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2
```

## Database Configuration

### PostgreSQL Setup

```bash
# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE social_media_agent;
CREATE USER sma_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE social_media_agent TO sma_user;
\q

# Initialize database tables
python scripts/init_database.py
```

### Redis Setup

```bash
# Install Redis
sudo apt install -y redis-server

# Configure Redis
sudo nano /etc/redis/redis.conf
# Set: bind 127.0.0.1
# Set: requirepass your_redis_password

# Restart Redis
sudo systemctl restart redis-server
sudo systemctl enable redis-server
```

## Application Deployment

### 1. Using Gunicorn (Recommended)

```bash
# Install Gunicorn
pip install gunicorn gevent

# Create Gunicorn configuration
cat > gunicorn.conf.py << EOF
bind = "0.0.0.0:5000"
workers = 4
worker_class = "gevent"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
preload_app = True
EOF

# Create systemd service
sudo tee /etc/systemd/system/social-media-agent.service << EOF
[Unit]
Description=Social Media Agent SaaS Platform
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/social-media-agent/saas-api-gateway
Environment=PATH=/home/ubuntu/social-media-agent/venv/bin
ExecStart=/home/ubuntu/social-media-agent/venv/bin/gunicorn -c gunicorn.conf.py src.main:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Start and enable service
sudo systemctl daemon-reload
sudo systemctl start social-media-agent
sudo systemctl enable social-media-agent
```

### 2. Using Docker (Alternative)

```bash
# Build Docker image
docker build -t social-media-agent:latest .

# Run container
docker run -d \
  --name social-media-agent \
  --env-file .env \
  -p 5000:5000 \
  --restart unless-stopped \
  social-media-agent:latest
```

### 3. Background Workers

```bash
# Install Celery
pip install celery

# Create Celery service
sudo tee /etc/systemd/system/celery-worker.service << EOF
[Unit]
Description=Celery Worker
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/social-media-agent/saas-api-gateway
Environment=PATH=/home/ubuntu/social-media-agent/venv/bin
ExecStart=/home/ubuntu/social-media-agent/venv/bin/celery -A src.main.celery worker --loglevel=info
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Start Celery worker
sudo systemctl start celery-worker
sudo systemctl enable celery-worker
```

## Frontend Deployment

### 1. Build and Deploy

```bash
# Build frontend
cd saas-frontend
npm run build

# Copy build files to web server
sudo cp -r dist/* /var/www/html/

# Or serve with Nginx (recommended)
sudo mkdir -p /var/www/social-media-agent
sudo cp -r dist/* /var/www/social-media-agent/
```

### 2. Nginx Configuration

```bash
# Create Nginx configuration
sudo tee /etc/nginx/sites-available/social-media-agent << EOF
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Frontend
    location / {
        root /var/www/social-media-agent;
        index index.html;
        try_files \$uri \$uri/ /index.html;
    }
    
    # API
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # Static files
    location /static/ {
        alias /home/ubuntu/social-media-agent/saas-api-gateway/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/social-media-agent /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## SSL/TLS Configuration

### Using Let's Encrypt (Recommended)

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## Monitoring and Logging

### 1. Application Logging

```bash
# Create log directory
sudo mkdir -p /var/log/social-media-agent
sudo chown ubuntu:ubuntu /var/log/social-media-agent

# Configure log rotation
sudo tee /etc/logrotate.d/social-media-agent << EOF
/var/log/social-media-agent/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 ubuntu ubuntu
}
EOF
```

### 2. System Monitoring

```bash
# Install monitoring tools
sudo apt install -y htop iotop nethogs

# Install Prometheus Node Exporter (optional)
wget https://github.com/prometheus/node_exporter/releases/download/v1.6.1/node_exporter-1.6.1.linux-amd64.tar.gz
tar xvfz node_exporter-1.6.1.linux-amd64.tar.gz
sudo cp node_exporter-1.6.1.linux-amd64/node_exporter /usr/local/bin/
sudo useradd --no-create-home --shell /bin/false node_exporter
sudo chown node_exporter:node_exporter /usr/local/bin/node_exporter

# Create systemd service for Node Exporter
sudo tee /etc/systemd/system/node_exporter.service << EOF
[Unit]
Description=Node Exporter
Wants=network-online.target
After=network-online.target

[Service]
User=node_exporter
Group=node_exporter
Type=simple
ExecStart=/usr/local/bin/node_exporter

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl start node_exporter
sudo systemctl enable node_exporter
```

## Backup and Recovery

### 1. Database Backup

```bash
# Create backup script
cat > /home/ubuntu/backup_db.sh << EOF
#!/bin/bash
BACKUP_DIR="/home/ubuntu/backups"
DATE=\$(date +%Y%m%d_%H%M%S)
mkdir -p \$BACKUP_DIR

# PostgreSQL backup
pg_dump -h localhost -U sma_user social_media_agent > \$BACKUP_DIR/db_backup_\$DATE.sql

# Compress backup
gzip \$BACKUP_DIR/db_backup_\$DATE.sql

# Upload to S3 (optional)
aws s3 cp \$BACKUP_DIR/db_backup_\$DATE.sql.gz s3://your-backup-bucket/database/

# Clean old backups (keep 30 days)
find \$BACKUP_DIR -name "db_backup_*.sql.gz" -mtime +30 -delete
EOF

chmod +x /home/ubuntu/backup_db.sh

# Schedule daily backups
crontab -e
# Add: 0 2 * * * /home/ubuntu/backup_db.sh
```

### 2. Application Backup

```bash
# Create application backup script
cat > /home/ubuntu/backup_app.sh << EOF
#!/bin/bash
BACKUP_DIR="/home/ubuntu/backups"
DATE=\$(date +%Y%m%d_%H%M%S)
APP_DIR="/home/ubuntu/social-media-agent"

# Create application backup
tar -czf \$BACKUP_DIR/app_backup_\$DATE.tar.gz -C \$APP_DIR .

# Upload to S3 (optional)
aws s3 cp \$BACKUP_DIR/app_backup_\$DATE.tar.gz s3://your-backup-bucket/application/

# Clean old backups
find \$BACKUP_DIR -name "app_backup_*.tar.gz" -mtime +7 -delete
EOF

chmod +x /home/ubuntu/backup_app.sh
```

## Scaling and Performance

### 1. Horizontal Scaling

```bash
# Load Balancer Configuration (Nginx)
upstream app_servers {
    server 10.0.1.10:5000;
    server 10.0.1.11:5000;
    server 10.0.1.12:5000;
}

server {
    location /api/ {
        proxy_pass http://app_servers;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }
}
```

### 2. Database Optimization

```sql
-- PostgreSQL optimization
-- Add to postgresql.conf
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200

-- Create indexes for better performance
CREATE INDEX idx_content_feedback_tenant_created ON content_feedback(tenant_id, created_at);
CREATE INDEX idx_social_connections_tenant_platform ON social_connections(tenant_id, platform);
CREATE INDEX idx_social_media_metrics_tenant_platform ON social_media_metrics(tenant_id, platform, created_at);
```

### 3. Redis Optimization

```bash
# Redis configuration optimization
# Add to /etc/redis/redis.conf
maxmemory 512mb
maxmemory-policy allkeys-lru
tcp-keepalive 300
timeout 0
```

## Security Considerations

### 1. Firewall Configuration

```bash
# Configure UFW firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

### 2. Security Headers

```nginx
# Add to Nginx configuration
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header X-Content-Type-Options "nosniff" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

### 3. Regular Security Updates

```bash
# Create update script
cat > /home/ubuntu/security_updates.sh << EOF
#!/bin/bash
sudo apt update
sudo apt upgrade -y
sudo apt autoremove -y
sudo apt autoclean
EOF

chmod +x /home/ubuntu/security_updates.sh

# Schedule weekly updates
crontab -e
# Add: 0 3 * * 0 /home/ubuntu/security_updates.sh
```

## Troubleshooting

### Common Issues

1. **Application won't start**
   ```bash
   # Check logs
   sudo journalctl -u social-media-agent -f
   
   # Check configuration
   python -c "from src.config.config_manager import ConfigManager; print('Config OK')"
   ```

2. **Database connection issues**
   ```bash
   # Test database connection
   psql -h localhost -U sma_user -d social_media_agent -c "SELECT 1;"
   
   # Check PostgreSQL status
   sudo systemctl status postgresql
   ```

3. **Redis connection issues**
   ```bash
   # Test Redis connection
   redis-cli ping
   
   # Check Redis logs
   sudo tail -f /var/log/redis/redis-server.log
   ```

4. **High memory usage**
   ```bash
   # Monitor memory usage
   htop
   
   # Check application memory
   ps aux | grep gunicorn
   
   # Restart application if needed
   sudo systemctl restart social-media-agent
   ```

### Performance Monitoring

```bash
# Monitor application performance
curl -s http://localhost:5000/health | jq .

# Monitor database performance
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity;"

# Monitor Redis performance
redis-cli info memory
```

## Maintenance

### Regular Maintenance Tasks

1. **Weekly Tasks**
   - Review application logs
   - Check disk space usage
   - Monitor database performance
   - Review security logs

2. **Monthly Tasks**
   - Update dependencies
   - Review backup integrity
   - Performance optimization
   - Security audit

3. **Quarterly Tasks**
   - Full system backup
   - Disaster recovery testing
   - Security penetration testing
   - Capacity planning review

### Health Checks

```bash
# Create health check script
cat > /home/ubuntu/health_check.sh << EOF
#!/bin/bash

echo "=== Social Media Agent Health Check ==="
echo "Date: \$(date)"
echo

# Check application
echo "Application Status:"
curl -s http://localhost:5000/health || echo "❌ Application not responding"

# Check database
echo "Database Status:"
pg_isready -h localhost -p 5432 && echo "✅ PostgreSQL is ready" || echo "❌ PostgreSQL not ready"

# Check Redis
echo "Redis Status:"
redis-cli ping > /dev/null && echo "✅ Redis is ready" || echo "❌ Redis not ready"

# Check disk space
echo "Disk Usage:"
df -h | grep -E '^/dev/'

# Check memory
echo "Memory Usage:"
free -h

echo "=== Health Check Complete ==="
EOF

chmod +x /home/ubuntu/health_check.sh
```

This deployment guide provides a comprehensive foundation for deploying the Social Media Agent SaaS platform in production. Adjust configurations based on your specific requirements and infrastructure setup.

