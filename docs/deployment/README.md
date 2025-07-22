# Deployment Guide

This comprehensive guide covers deploying the Social Media Agent system across various environments, from local development to production-scale deployments.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development](#local-development)
3. [Docker Deployment](#docker-deployment)
4. [Cloud Deployments](#cloud-deployments)
5. [Kubernetes](#kubernetes)
6. [Monitoring and Observability](#monitoring-and-observability)
7. [Security Considerations](#security-considerations)
8. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

#### Minimum Requirements
- **CPU**: 2 cores
- **RAM**: 4GB
- **Storage**: 20GB
- **Network**: Stable internet connection

#### Recommended Requirements
- **CPU**: 4+ cores
- **RAM**: 8GB+
- **Storage**: 50GB+ SSD
- **Network**: High-speed internet connection

#### Production Requirements
- **CPU**: 8+ cores
- **RAM**: 16GB+
- **Storage**: 100GB+ SSD with backup
- **Network**: Redundant internet connections
- **Load Balancer**: For high availability
- **Database**: Dedicated database server

### Software Dependencies

#### Required Software
- **Python**: 3.9 or higher
- **Docker**: 20.10+ (for containerized deployment)
- **Git**: For source code management
- **PostgreSQL**: 13+ (for production)
- **Redis**: 6+ (for caching and task queue)

#### Optional Software
- **Kubernetes**: 1.20+ (for orchestration)
- **Nginx**: For reverse proxy
- **Prometheus**: For monitoring
- **Grafana**: For dashboards

### API Keys and Credentials

Before deployment, ensure you have:

1. **LLM Provider API Keys**:
   - OpenAI API key
   - Anthropic API key (optional)
   - Google AI API key (optional)

2. **Social Media Platform Credentials**:
   - Facebook App ID, App Secret, Access Token
   - Twitter API keys and tokens
   - Instagram Business Account credentials
   - LinkedIn API credentials
   - TikTok Developer credentials

3. **Infrastructure Credentials**:
   - Cloud provider credentials (AWS, GCP, Azure)
   - Database connection strings
   - Monitoring service keys

## Local Development

### Quick Start

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-org/social-media-agent.git
   cd social-media-agent
   ```

2. **Set up Python environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

3. **Configure environment**:
   ```bash
   cp examples/config.example.yaml config/config.yaml
   cp .env.example .env
   ```

4. **Edit configuration files**:
   ```yaml
   # config/config.yaml
   general:
     app_name: "Social Media Agent Dev"
     environment: "development"
     debug: true
   
   llm_providers:
     openai:
       api_key: "${OPENAI_API_KEY}"
   
   platforms:
     facebook:
       enabled: true
       api_credentials:
         access_token: "${FACEBOOK_ACCESS_TOKEN}"
   ```

5. **Set environment variables**:
   ```bash
   # .env
   OPENAI_API_KEY=your_openai_api_key
   FACEBOOK_ACCESS_TOKEN=your_facebook_token
   DATABASE_URL=sqlite:///./data/social_media_agent.db
   REDIS_URL=redis://localhost:6379/0
   ```

6. **Initialize database**:
   ```bash
   python scripts/init_database.py
   ```

7. **Run the application**:
   ```bash
   python -m src.main
   ```

### Development Tools

#### Pre-commit Hooks
```bash
pre-commit install
pre-commit run --all-files
```

#### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test categories
pytest tests/unit/ -v
pytest tests/integration/ -v
```

#### Code Quality
```bash
# Format code
black src/ tests/
isort src/ tests/

# Lint code
flake8 src/ tests/
mypy src/

# Security check
bandit -r src/
```

## Docker Deployment

### Single Container Deployment

1. **Build the Docker image**:
   ```bash
   docker build -t social-media-agent:latest .
   ```

2. **Run the container**:
   ```bash
   docker run -d \
     --name social-media-agent \
     -p 8000:8000 \
     -v $(pwd)/config:/app/config \
     -v $(pwd)/data:/app/data \
     -v $(pwd)/logs:/app/logs \
     -e OPENAI_API_KEY=your_key \
     -e FACEBOOK_ACCESS_TOKEN=your_token \
     social-media-agent:latest
   ```

### Docker Compose Deployment

1. **Create docker-compose.yml**:
   ```yaml
   version: '3.8'
   
   services:
     social-media-agent:
       build: .
       ports:
         - "8000:8000"
       volumes:
         - ./config:/app/config
         - ./data:/app/data
         - ./logs:/app/logs
       environment:
         - ENVIRONMENT=production
         - DATABASE_URL=postgresql://postgres:password@db:5432/social_media_agent
         - REDIS_URL=redis://redis:6379/0
       depends_on:
         - db
         - redis
       restart: unless-stopped
       healthcheck:
         test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8000/health')"]
         interval: 30s
         timeout: 10s
         retries: 3
   
     db:
       image: postgres:15
       environment:
         POSTGRES_DB: social_media_agent
         POSTGRES_USER: postgres
         POSTGRES_PASSWORD: password
       volumes:
         - postgres_data:/var/lib/postgresql/data
         - ./scripts/init.sql:/docker-entrypoint-initdb.d/init.sql
       restart: unless-stopped
       healthcheck:
         test: ["CMD-SHELL", "pg_isready -U postgres"]
         interval: 10s
         timeout: 5s
         retries: 5
   
     redis:
       image: redis:7-alpine
       volumes:
         - redis_data:/data
       restart: unless-stopped
       healthcheck:
         test: ["CMD", "redis-cli", "ping"]
         interval: 10s
         timeout: 5s
         retries: 3
   
     nginx:
       image: nginx:alpine
       ports:
         - "80:80"
         - "443:443"
       volumes:
         - ./nginx/nginx.conf:/etc/nginx/nginx.conf
         - ./nginx/ssl:/etc/nginx/ssl
       depends_on:
         - social-media-agent
       restart: unless-stopped
   
   volumes:
     postgres_data:
     redis_data:
   
   networks:
     default:
       driver: bridge
   ```

2. **Deploy with Docker Compose**:
   ```bash
   docker-compose up -d
   ```

3. **Monitor deployment**:
   ```bash
   docker-compose logs -f
   docker-compose ps
   ```

### Multi-Stage Production Build

```dockerfile
# Production Dockerfile with multi-stage build
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Build stage
FROM base as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Production stage
FROM base as production

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy dependencies from builder
COPY --from=builder /root/.local /home/appuser/.local

# Set up application
WORKDIR /app
COPY --chown=appuser:appuser . .

# Create necessary directories
RUN mkdir -p /app/logs /app/data /app/config \
    && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Add local bin to PATH
ENV PATH=/home/appuser/.local/bin:$PATH

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Expose port
EXPOSE 8000

# Start application
CMD ["python", "-m", "src.main"]
```

## Cloud Deployments

### AWS Deployment

#### AWS ECS (Elastic Container Service)

1. **Create ECS Task Definition**:
   ```json
   {
     "family": "social-media-agent",
     "networkMode": "awsvpc",
     "requiresCompatibilities": ["FARGATE"],
     "cpu": "1024",
     "memory": "2048",
     "executionRoleArn": "arn:aws:iam::ACCOUNT:role/ecsTaskExecutionRole",
     "taskRoleArn": "arn:aws:iam::ACCOUNT:role/ecsTaskRole",
     "containerDefinitions": [
       {
         "name": "social-media-agent",
         "image": "your-account.dkr.ecr.region.amazonaws.com/social-media-agent:latest",
         "portMappings": [
           {
             "containerPort": 8000,
             "protocol": "tcp"
           }
         ],
         "environment": [
           {
             "name": "ENVIRONMENT",
             "value": "production"
           }
         ],
         "secrets": [
           {
             "name": "OPENAI_API_KEY",
             "valueFrom": "arn:aws:secretsmanager:region:account:secret:social-media-agent/openai-key"
           },
           {
             "name": "DATABASE_URL",
             "valueFrom": "arn:aws:secretsmanager:region:account:secret:social-media-agent/database-url"
           }
         ],
         "logConfiguration": {
           "logDriver": "awslogs",
           "options": {
             "awslogs-group": "/ecs/social-media-agent",
             "awslogs-region": "us-west-2",
             "awslogs-stream-prefix": "ecs"
           }
         },
         "healthCheck": {
           "command": [
             "CMD-SHELL",
             "python -c \"import requests; requests.get('http://localhost:8000/health')\""
           ],
           "interval": 30,
           "timeout": 5,
           "retries": 3,
           "startPeriod": 60
         }
       }
     ]
   }
   ```

2. **Create ECS Service**:
   ```bash
   aws ecs create-service \
     --cluster social-media-agent-cluster \
     --service-name social-media-agent-service \
     --task-definition social-media-agent:1 \
     --desired-count 2 \
     --launch-type FARGATE \
     --network-configuration "awsvpcConfiguration={subnets=[subnet-12345,subnet-67890],securityGroups=[sg-abcdef],assignPublicIp=ENABLED}" \
     --load-balancers "targetGroupArn=arn:aws:elasticloadbalancing:region:account:targetgroup/social-media-agent/1234567890,containerName=social-media-agent,containerPort=8000"
   ```

#### AWS Lambda (Serverless)

1. **Create Lambda deployment package**:
   ```bash
   # Create deployment package
   mkdir lambda-package
   pip install -r requirements.txt -t lambda-package/
   cp -r src/ lambda-package/
   cd lambda-package && zip -r ../social-media-agent-lambda.zip .
   ```

2. **Deploy with AWS SAM**:
   ```yaml
   # template.yaml
   AWSTemplateFormatVersion: '2010-09-09'
   Transform: AWS::Serverless-2016-10-31
   
   Resources:
     SocialMediaAgentFunction:
       Type: AWS::Serverless::Function
       Properties:
         CodeUri: social-media-agent-lambda.zip
         Handler: src.lambda_handler.handler
         Runtime: python3.11
         Timeout: 900
         MemorySize: 1024
         Environment:
           Variables:
             ENVIRONMENT: production
         Events:
           ScheduledEvent:
             Type: Schedule
             Properties:
               Schedule: rate(1 hour)
               Input: '{"action": "create_posts"}'
   ```

### Google Cloud Platform (GCP)

#### Google Cloud Run

1. **Build and push to Container Registry**:
   ```bash
   # Build image
   docker build -t gcr.io/PROJECT_ID/social-media-agent:latest .
   
   # Push to registry
   docker push gcr.io/PROJECT_ID/social-media-agent:latest
   ```

2. **Deploy to Cloud Run**:
   ```bash
   gcloud run deploy social-media-agent \
     --image gcr.io/PROJECT_ID/social-media-agent:latest \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars ENVIRONMENT=production \
     --set-secrets OPENAI_API_KEY=openai-key:latest \
     --memory 2Gi \
     --cpu 2 \
     --max-instances 10
   ```

#### Google Kubernetes Engine (GKE)

1. **Create GKE cluster**:
   ```bash
   gcloud container clusters create social-media-agent-cluster \
     --zone us-central1-a \
     --num-nodes 3 \
     --enable-autoscaling \
     --min-nodes 1 \
     --max-nodes 10
   ```

2. **Deploy application**:
   ```yaml
   # k8s/deployment.yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: social-media-agent
   spec:
     replicas: 3
     selector:
       matchLabels:
         app: social-media-agent
     template:
       metadata:
         labels:
           app: social-media-agent
       spec:
         containers:
         - name: social-media-agent
           image: gcr.io/PROJECT_ID/social-media-agent:latest
           ports:
           - containerPort: 8000
           env:
           - name: ENVIRONMENT
             value: "production"
           - name: OPENAI_API_KEY
             valueFrom:
               secretKeyRef:
                 name: api-keys
                 key: openai-key
   ```

### Microsoft Azure

#### Azure Container Instances (ACI)

```bash
az container create \
  --resource-group social-media-agent-rg \
  --name social-media-agent \
  --image your-registry.azurecr.io/social-media-agent:latest \
  --cpu 2 \
  --memory 4 \
  --ports 8000 \
  --environment-variables ENVIRONMENT=production \
  --secure-environment-variables OPENAI_API_KEY=your-key
```

#### Azure Kubernetes Service (AKS)

1. **Create AKS cluster**:
   ```bash
   az aks create \
     --resource-group social-media-agent-rg \
     --name social-media-agent-cluster \
     --node-count 3 \
     --enable-addons monitoring \
     --generate-ssh-keys
   ```

2. **Deploy application**:
   ```bash
   kubectl apply -f k8s/
   ```

## Kubernetes

### Complete Kubernetes Deployment

#### Namespace and ConfigMap

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: social-media-agent

---
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: social-media-agent-config
  namespace: social-media-agent
data:
  config.yaml: |
    general:
      app_name: "Social Media Agent"
      environment: "production"
      debug: false
    
    llm_providers:
      openai:
        api_base: "https://api.openai.com/v1"
        models:
          text: "gpt-4"
          image: "dall-e-3"
    
    platforms:
      facebook:
        enabled: true
      twitter:
        enabled: true
      linkedin:
        enabled: true
```

#### Secrets

```yaml
# k8s/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: social-media-agent-secrets
  namespace: social-media-agent
type: Opaque
data:
  openai-api-key: <base64-encoded-key>
  facebook-access-token: <base64-encoded-token>
  database-url: <base64-encoded-url>
```

#### Deployment

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: social-media-agent
  namespace: social-media-agent
  labels:
    app: social-media-agent
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 1
  selector:
    matchLabels:
      app: social-media-agent
  template:
    metadata:
      labels:
        app: social-media-agent
    spec:
      containers:
      - name: social-media-agent
        image: social-media-agent:latest
        ports:
        - containerPort: 8000
          name: http
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: social-media-agent-secrets
              key: openai-api-key
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: social-media-agent-secrets
              key: database-url
        volumeMounts:
        - name: config
          mountPath: /app/config
        - name: data
          mountPath: /app/data
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
      volumes:
      - name: config
        configMap:
          name: social-media-agent-config
      - name: data
        persistentVolumeClaim:
          claimName: social-media-agent-data
```

#### Service and Ingress

```yaml
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: social-media-agent-service
  namespace: social-media-agent
spec:
  selector:
    app: social-media-agent
  ports:
  - port: 80
    targetPort: 8000
    name: http
  type: ClusterIP

---
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: social-media-agent-ingress
  namespace: social-media-agent
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/rate-limit: "100"
spec:
  tls:
  - hosts:
    - social-media-agent.yourdomain.com
    secretName: social-media-agent-tls
  rules:
  - host: social-media-agent.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: social-media-agent-service
            port:
              number: 80
```

#### Persistent Volume

```yaml
# k8s/pvc.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: social-media-agent-data
  namespace: social-media-agent
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 50Gi
  storageClassName: fast-ssd
```

#### HorizontalPodAutoscaler

```yaml
# k8s/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: social-media-agent-hpa
  namespace: social-media-agent
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: social-media-agent
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### Deployment Commands

```bash
# Apply all Kubernetes manifests
kubectl apply -f k8s/

# Check deployment status
kubectl get pods -n social-media-agent
kubectl get services -n social-media-agent
kubectl get ingress -n social-media-agent

# View logs
kubectl logs -f deployment/social-media-agent -n social-media-agent

# Scale deployment
kubectl scale deployment social-media-agent --replicas=5 -n social-media-agent

# Update deployment
kubectl set image deployment/social-media-agent social-media-agent=social-media-agent:v2.0 -n social-media-agent

# Rollback deployment
kubectl rollout undo deployment/social-media-agent -n social-media-agent
```

## Monitoring and Observability

### Prometheus and Grafana

#### Prometheus Configuration

```yaml
# monitoring/prometheus.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
    
    scrape_configs:
    - job_name: 'social-media-agent'
      static_configs:
      - targets: ['social-media-agent-service:80']
      metrics_path: /metrics
      scrape_interval: 30s
```

#### Grafana Dashboard

```json
{
  "dashboard": {
    "title": "Social Media Agent Dashboard",
    "panels": [
      {
        "title": "Posts Created",
        "type": "stat",
        "targets": [
          {
            "expr": "sum(posts_created_total)",
            "legendFormat": "Total Posts"
          }
        ]
      },
      {
        "title": "Engagement Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "avg(engagement_rate)",
            "legendFormat": "Average Engagement Rate"
          }
        ]
      },
      {
        "title": "Agent Status",
        "type": "table",
        "targets": [
          {
            "expr": "agent_status",
            "legendFormat": "{{agent_name}}"
          }
        ]
      }
    ]
  }
}
```

### Logging

#### Centralized Logging with ELK Stack

```yaml
# logging/elasticsearch.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: elasticsearch
spec:
  replicas: 1
  selector:
    matchLabels:
      app: elasticsearch
  template:
    metadata:
      labels:
        app: elasticsearch
    spec:
      containers:
      - name: elasticsearch
        image: docker.elastic.co/elasticsearch/elasticsearch:8.5.0
        ports:
        - containerPort: 9200
        env:
        - name: discovery.type
          value: single-node
        - name: ES_JAVA_OPTS
          value: "-Xms512m -Xmx512m"

---
# logging/logstash.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: logstash-config
data:
  logstash.conf: |
    input {
      beats {
        port => 5044
      }
    }
    
    filter {
      if [fields][service] == "social-media-agent" {
        json {
          source => "message"
        }
      }
    }
    
    output {
      elasticsearch {
        hosts => ["elasticsearch:9200"]
        index => "social-media-agent-%{+YYYY.MM.dd}"
      }
    }
```

### Health Checks and Alerts

#### Health Check Endpoints

```python
# src/health.py
from fastapi import FastAPI
from src.agents.team_leader import TeamLeader

app = FastAPI()

@app.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@app.get("/ready")
async def readiness_check():
    """Readiness check for Kubernetes."""
    # Check if all agents are ready
    team_leader = TeamLeader.get_instance()
    agent_status = await team_leader.check_agent_health()
    
    if all(status["healthy"] for status in agent_status.values()):
        return {"status": "ready"}
    else:
        return {"status": "not ready", "details": agent_status}, 503

@app.get("/metrics")
async def metrics_endpoint():
    """Prometheus metrics endpoint."""
    # Return metrics in Prometheus format
    metrics = await collect_prometheus_metrics()
    return Response(content=metrics, media_type="text/plain")
```

#### Alerting Rules

```yaml
# monitoring/alerts.yaml
groups:
- name: social-media-agent
  rules:
  - alert: AgentDown
    expr: up{job="social-media-agent"} == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "Social Media Agent is down"
      description: "Social Media Agent has been down for more than 1 minute"
  
  - alert: HighErrorRate
    expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "High error rate detected"
      description: "Error rate is {{ $value }} errors per second"
  
  - alert: LowEngagementRate
    expr: avg(engagement_rate) < 1.0
    for: 10m
    labels:
      severity: warning
    annotations:
      summary: "Low engagement rate"
      description: "Average engagement rate is below 1.0%"
```

## Security Considerations

### Security Best Practices

1. **API Key Management**:
   - Use environment variables or secret management systems
   - Rotate API keys regularly
   - Never commit keys to version control

2. **Network Security**:
   - Use HTTPS/TLS for all communications
   - Implement proper firewall rules
   - Use VPCs and private subnets

3. **Container Security**:
   - Use non-root users in containers
   - Scan images for vulnerabilities
   - Keep base images updated

4. **Access Control**:
   - Implement RBAC (Role-Based Access Control)
   - Use least privilege principle
   - Enable audit logging

### Security Configuration

#### SSL/TLS Configuration

```nginx
# nginx/nginx.conf
server {
    listen 443 ssl http2;
    server_name social-media-agent.yourdomain.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    location / {
        proxy_pass http://social-media-agent:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### Network Policies (Kubernetes)

```yaml
# k8s/network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: social-media-agent-netpol
  namespace: social-media-agent
spec:
  podSelector:
    matchLabels:
      app: social-media-agent
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to: []
    ports:
    - protocol: TCP
      port: 443  # HTTPS
    - protocol: TCP
      port: 80   # HTTP
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Application Won't Start

**Symptoms**:
- Container exits immediately
- "Configuration error" messages
- Import errors

**Solutions**:
```bash
# Check logs
docker logs social-media-agent
kubectl logs deployment/social-media-agent -n social-media-agent

# Verify configuration
python -c "from src.config import ConfigManager; ConfigManager('config/config.yaml').validate_config()"

# Check dependencies
pip check
```

#### 2. API Rate Limiting

**Symptoms**:
- "Rate limit exceeded" errors
- Slow response times
- Failed posts

**Solutions**:
```python
# Implement exponential backoff
import asyncio
import random

async def retry_with_backoff(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await func()
        except RateLimitError:
            if attempt == max_retries - 1:
                raise
            wait_time = (2 ** attempt) + random.uniform(0, 1)
            await asyncio.sleep(wait_time)
```

#### 3. Database Connection Issues

**Symptoms**:
- "Connection refused" errors
- Timeout errors
- Data not persisting

**Solutions**:
```bash
# Check database connectivity
psql $DATABASE_URL -c "SELECT 1;"

# Verify database schema
python scripts/check_schema.py

# Reset database (development only)
python scripts/reset_database.py
```

#### 4. Memory Issues

**Symptoms**:
- Out of memory errors
- Slow performance
- Container restarts

**Solutions**:
```yaml
# Increase memory limits
resources:
  limits:
    memory: "4Gi"
  requests:
    memory: "2Gi"

# Enable memory profiling
environment:
  - name: PYTHONMALLOC
    value: "debug"
```

#### 5. SSL/TLS Certificate Issues

**Symptoms**:
- Certificate validation errors
- HTTPS not working
- Browser security warnings

**Solutions**:
```bash
# Check certificate validity
openssl x509 -in cert.pem -text -noout

# Renew Let's Encrypt certificate
certbot renew --dry-run

# Update certificate in Kubernetes
kubectl create secret tls social-media-agent-tls \
  --cert=cert.pem --key=key.pem \
  -n social-media-agent
```

### Debugging Tools

#### Application Debugging

```python
# Enable debug mode
import logging
logging.basicConfig(level=logging.DEBUG)

# Add performance monitoring
import time
import functools

def monitor_performance(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} took {end_time - start_time:.2f} seconds")
        return result
    return wrapper
```

#### Infrastructure Debugging

```bash
# Kubernetes debugging
kubectl describe pod <pod-name> -n social-media-agent
kubectl get events -n social-media-agent --sort-by='.lastTimestamp'

# Docker debugging
docker exec -it social-media-agent /bin/bash
docker stats social-media-agent

# Network debugging
kubectl port-forward service/social-media-agent-service 8080:80 -n social-media-agent
curl -v http://localhost:8080/health
```

### Performance Optimization

#### Database Optimization

```sql
-- Create indexes for better performance
CREATE INDEX idx_posts_created_at ON posts(created_at);
CREATE INDEX idx_metrics_agent_platform ON metrics(agent_name, platform);
CREATE INDEX idx_posts_platform_status ON posts(platform, status);

-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM posts WHERE platform = 'facebook' AND created_at > NOW() - INTERVAL '7 days';
```

#### Application Optimization

```python
# Use connection pooling
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True
)

# Implement caching
from functools import lru_cache
import redis

redis_client = redis.Redis.from_url(REDIS_URL)

@lru_cache(maxsize=128)
def get_platform_config(platform: str):
    return config_manager.get_platform_config(platform)

# Use async/await properly
async def process_posts_concurrently(posts):
    tasks = [process_post(post) for post in posts]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results
```

For additional support and troubleshooting, see:
- [GitHub Issues](https://github.com/your-org/social-media-agent/issues)
- [Documentation](../README.md)
- [API Reference](../api/README.md)

