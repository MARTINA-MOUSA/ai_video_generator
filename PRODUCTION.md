# Production Deployment Guide

## Prerequisites

- Docker and Docker Compose installed
- Domain name (optional, for SSL)
- SSL certificates (optional, for HTTPS)

## Quick Start with Docker

### 1. Environment Setup

Create `.env` with production values:

```env
# Database
POSTGRES_DB=ai_video_generator
POSTGRES_USER=postgres
POSTGRES_PASSWORD=strong_password_here

# Application
DEBUG=False
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000

# Minimax API
MINIMAX_API_KEY=sk-xxxxxxxxxxxxxxxx
MINIMAX_MODEL=MiniMax-Hailuo-2.3
MINIMAX_BASE_URL=https://api.minimax.io/v1

# Security
MAX_REQUESTS_PER_MINUTE=10
```

### 2. Build and Start

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

### 3. Access Services

- **Frontend**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Nginx** (if enabled): http://localhost

## Production Configuration

### Database Migration

```bash
# Run migrations (if using Alembic)
docker-compose exec backend alembic upgrade head

# Or create tables manually
docker-compose exec backend python -c "from backend.core.database import init_db; init_db()"
```

### SSL/HTTPS Setup

1. **Get SSL certificates** (Let's Encrypt recommended):
```bash
certbot certonly --standalone -d yourdomain.com
```

2. **Update nginx.conf** for HTTPS:
```nginx
server {
    listen 443 ssl;
    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    # ... rest of config
}
```

3. **Mount SSL certificates** in docker-compose.yml:
```yaml
volumes:
  - /etc/letsencrypt:/etc/nginx/ssl:ro
```

### Environment Variables

**Required:**
- `MINIMAX_API_KEY` - Minimax API key
- `POSTGRES_PASSWORD` - Database password
- `DATABASE_URL` - PostgreSQL connection string

**Optional:**
- `CELERY_BROKER_URL` - Redis connection
- `CELERY_RESULT_BACKEND` - Redis connection

### Scaling

**Scale backend workers:**
```bash
docker-compose up -d --scale backend=3
```

**Update gunicorn workers:**
```env
WORKERS=4  # In .env file
```

## Monitoring

### Health Checks

```bash
# Backend health
curl http://localhost:8000/api/health

# Database connection
docker-compose exec backend python -c "from backend.core.database import engine; print(engine.connect())"
```

### Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 backend
```

### Resource Usage

```bash
# Container stats
docker stats

# Disk usage
docker system df
```

## Backup & Recovery

### Database Backup

```bash
# Backup
docker-compose exec db pg_dump -U postgres ai_video_generator > backup.sql

# Restore
docker-compose exec -T db psql -U postgres ai_video_generator < backup.sql
```

### Video Files Backup

```bash
# Backup outputs directory
tar -czf outputs_backup.tar.gz outputs/

# Restore
tar -xzf outputs_backup.tar.gz
```

## Security Checklist

- [ ] Change default PostgreSQL password
- [ ] Use strong API keys
- [ ] Enable HTTPS/SSL
- [ ] Configure firewall rules
- [ ] Set up rate limiting
- [ ] Enable CORS only for trusted domains
- [ ] Regular security updates
- [ ] Monitor logs for suspicious activity
- [ ] Backup database regularly
- [ ] Use environment variables for secrets

## Performance Optimization

### Database

```sql
-- Add indexes (run in PostgreSQL)
CREATE INDEX idx_video_jobs_status ON video_jobs(status);
CREATE INDEX idx_video_jobs_created_at ON video_jobs(created_at);
CREATE INDEX idx_video_files_created_at ON video_files(created_at);
```

### Caching

Enable Redis caching for frequently accessed data.

### CDN

Use CDN for serving generated videos (AWS S3, Cloudflare, etc.)

## Troubleshooting

### Container won't start

```bash
# Check logs
docker-compose logs backend

# Check container status
docker-compose ps

# Restart service
docker-compose restart backend
```

### Database connection issues

```bash
# Check database is running
docker-compose ps db

# Test connection
docker-compose exec backend python -c "from backend.core.database import engine; engine.connect()"
```

### Out of memory

```bash
# Check memory usage
docker stats

# Reduce workers
# Edit .env: WORKERS=2
docker-compose restart backend
```

## Deployment to Cloud

### AWS

1. Use ECS/EKS for container orchestration
2. RDS for PostgreSQL
3. ElastiCache for Redis
4. S3 for video storage
5. CloudFront for CDN

### Google Cloud

1. Cloud Run for containers
2. Cloud SQL for PostgreSQL
3. Memorystore for Redis
4. Cloud Storage for videos
5. Cloud CDN

### Azure

1. Container Instances or AKS
2. Azure Database for PostgreSQL
3. Azure Cache for Redis
4. Blob Storage for videos
5. Azure CDN

## Maintenance

### Update Application

```bash
# Pull latest code
git pull

# Rebuild containers
docker-compose build

# Restart services
docker-compose up -d
```

### Clean Up

```bash
# Remove old containers
docker-compose down

# Remove volumes (WARNING: deletes data)
docker-compose down -v

# Clean up old images
docker image prune -a
```

## Support

For issues or questions:
- Check logs: `docker-compose logs`
- Review configuration files
- Check GitHub issues

