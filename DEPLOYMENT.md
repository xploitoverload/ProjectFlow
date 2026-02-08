# 🚀 Deployment Guide - Project Management System

This guide provides comprehensive instructions for deploying the Project Management System to various platforms.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start with Docker](#quick-start-with-docker)
- [Platform-Specific Deployments](#platform-specific-deployments)
  - [Render.com](#rendercom)
  - [Heroku](#heroku)
  - [Railway.app](#railwayapp)
  - [DigitalOcean App Platform](#digitalocean-app-platform)
  - [AWS Elastic Beanstalk](#aws-elastic-beanstalk)
  - [Google Cloud Run](#google-cloud-run)
- [Manual VPS Deployment](#manual-vps-deployment)
- [Environment Variables](#environment-variables)
- [Post-Deployment Steps](#post-deployment-steps)
- [Troubleshooting](#troubleshooting)

## Prerequisites

Before deploying, ensure you have:

- Git installed
- Account on your chosen platform
- Basic understanding of terminal/command line

## Quick Start with Docker

The fastest way to deploy locally or on any Docker-compatible platform:

### Local Docker Deployment

```bash
# 1. Clone the repository
git clone https://github.com/xploitoverload/project-management.git
cd project-management

# 2. Create environment file
cp .env.example .env
# Edit .env with your configurations

# 3. Build and run with Docker Compose
docker-compose up -d

# 4. Access the application
# http://localhost:8000
```

### Production Docker Deployment

```bash
# Build production image
docker build -t project-management:latest .

# Run with environment variables
docker run -d \
  -p 8000:8000 \
  -e FLASK_ENV=production \
  -e SECRET_KEY=your-super-secret-key \
  -e DATABASE_URL=your-database-url \
  --name project-management \
  project-management:latest
```

## Platform-Specific Deployments

### Render.com

**Free tier available, easy setup, automatic HTTPS**

#### Automatic Deployment (Recommended)

1. Fork or push this repository to GitHub
2. Go to [Render Dashboard](https://dashboard.render.com/)
3. Click "New +" → "Blueprint"
4. Connect your GitHub repository
5. Render will automatically detect `render.yaml` and create:
   - Web service
   - Redis instance
6. Set required environment variables:
   - `SECRET_KEY` (auto-generated)
   - `DATABASE_URL` (optional, defaults to SQLite)
7. Click "Apply"
8. Wait for deployment (3-5 minutes)
9. Access your app at: `https://your-app-name.onrender.com`

#### Manual Deployment

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New +" → "Web Service"
3. Connect your repository
4. Configure:
   - **Name**: project-management
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn run:app --bind 0.0.0.0:$PORT --workers 2`
5. Add environment variables (see [Environment Variables](#environment-variables))
6. Click "Create Web Service"

### Heroku

**Free tier available (with credit card), mature platform**

```bash
# 1. Install Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# 2. Login to Heroku
heroku login

# 3. Create new Heroku app
heroku create your-app-name

# 4. Add Redis addon (optional but recommended)
heroku addons:create heroku-redis:mini

# 5. Set environment variables
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")

# 6. Deploy
git push heroku main

# 7. Open app
heroku open

# 8. View logs
heroku logs --tail
```

### Railway.app

**Modern platform, generous free tier**

#### Using Railway CLI

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Initialize project
railway init

# 4. Add Redis plugin
railway add

# 5. Deploy
railway up

# 6. Set environment variables
railway variables set SECRET_KEY=your-secret-key

# 7. Get deployment URL
railway domain
```

#### Using Web Dashboard

1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Railway auto-detects Python app
5. Add Redis from the "New" button
6. Set environment variables
7. Deploy automatically starts

### DigitalOcean App Platform

**$5/month minimum, excellent performance**

1. Go to [DigitalOcean Apps](https://cloud.digitalocean.com/apps)
2. Click "Create App"
3. Connect GitHub repository
4. Configure:
   - **Type**: Web Service
   - **Branch**: main
   - **Build Command**: `pip install -r requirements.txt`
   - **Run Command**: `gunicorn run:app --bind 0.0.0.0:$PORT --workers 2`
5. Add Redis database (optional)
6. Set environment variables
7. Choose plan ($5/month starter recommended)
8. Launch app

### AWS Elastic Beanstalk

**Enterprise-grade, pay-as-you-go pricing**

```bash
# 1. Install EB CLI
pip install awsebcli

# 2. Initialize EB application
eb init -p python-3.11 project-management

# 3. Create environment
eb create project-management-prod

# 4. Set environment variables
eb setenv FLASK_ENV=production SECRET_KEY=your-secret-key

# 5. Deploy updates
eb deploy

# 6. Open application
eb open

# 7. View logs
eb logs
```

### Google Cloud Run

**Serverless, pay-per-use, scales to zero**

```bash
# 1. Install gcloud CLI
# https://cloud.google.com/sdk/docs/install

# 2. Login and set project
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# 3. Build container
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/project-management

# 4. Deploy to Cloud Run
gcloud run deploy project-management \
  --image gcr.io/YOUR_PROJECT_ID/project-management \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars FLASK_ENV=production,SECRET_KEY=your-secret-key

# 5. Get service URL
gcloud run services describe project-management --region us-central1
```

## Manual VPS Deployment

**For VPS providers like Linode, Vultr, or custom servers**

### Prerequisites

- Ubuntu 20.04+ or Debian 11+
- Root or sudo access
- Domain name (optional)

### Step-by-Step

```bash
# 1. Update system
sudo apt update && sudo apt upgrade -y

# 2. Install dependencies
sudo apt install -y python3 python3-pip python3-venv nginx redis-server supervisor

# 3. Clone repository
cd /opt
sudo git clone https://github.com/xploitoverload/project-management.git
cd project-management

# 4. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 5. Install Python packages
pip install -r requirements.txt
pip install gunicorn

# 6. Configure environment
sudo cp .env.example .env
sudo nano .env  # Edit with your settings

# 7. Create systemd service
sudo nano /etc/systemd/system/project-management.service
```

**Service file content:**

```ini
[Unit]
Description=Project Management System
After=network.target

[Service]
User=www-data
WorkingDirectory=/opt/project-management
Environment="PATH=/opt/project-management/venv/bin"
ExecStart=/opt/project-management/venv/bin/gunicorn --workers 4 --bind 127.0.0.1:8000 run:app
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# 8. Start service
sudo systemctl daemon-reload
sudo systemctl enable project-management
sudo systemctl start project-management
sudo systemctl status project-management

# 9. Configure Nginx
sudo nano /etc/nginx/sites-available/project-management
```

**Nginx configuration:**

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /opt/project-management/static;
    }
}
```

```bash
# 10. Enable Nginx site
sudo ln -s /etc/nginx/sites-available/project-management /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# 11. Setup SSL with Let's Encrypt (optional)
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## Environment Variables

Required environment variables for production deployment:

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `FLASK_ENV` | Yes | Environment mode | `production` |
| `SECRET_KEY` | Yes | Flask secret key | Generate with `python -c "import secrets; print(secrets.token_hex(32))"` |
| `DATABASE_URL` | No | Database connection string | `postgresql://user:pass@host/db` or `sqlite:///instance/app.db` |
| `REDIS_URL` | No | Redis connection string | `redis://localhost:6379/0` |
| `PORT` | No | Port to run on | `8000` (auto-set on most platforms) |
| `ADMIN_TOKEN` | No | Admin panel access token | Random secure string |
| `MAX_CONTENT_LENGTH` | No | Max upload size in bytes | `16777216` (16MB) |

### Generating a Secure SECRET_KEY

```bash
# Python
python -c "import secrets; print(secrets.token_hex(32))"

# OpenSSL
openssl rand -hex 32

# Online (not recommended for production)
# Use https://randomkeygen.com/
```

## Post-Deployment Steps

### 1. Initialize Database

```bash
# For Docker
docker-compose exec web python -c "from app import create_app, db; app=create_app(); app.app_context().push(); db.create_all()"

# For Heroku
heroku run python -c "from app import create_app, db; app=create_app(); app.app_context().push(); db.create_all()"

# For manual deployment
cd /opt/project-management
source venv/bin/activate
python -c "from app import create_app, db; app=create_app(); app.app_context().push(); db.create_all()"
```

### 2. Create Admin User

```bash
# Access admin registration with admin token
# https://your-app.com/admin/register?token=YOUR_ADMIN_TOKEN
```

### 3. Configure Domain (if applicable)

- Point your domain's DNS to your deployment IP/URL
- Update `A` record or `CNAME` record
- Wait for DNS propagation (up to 48 hours)

### 4. Enable HTTPS

Most platforms provide automatic HTTPS. For manual deployments:

```bash
# Using Certbot (Let's Encrypt)
sudo certbot --nginx -d your-domain.com
sudo certbot renew --dry-run  # Test renewal
```

### 5. Set Up Monitoring

- Configure application monitoring (Sentry, New Relic, etc.)
- Set up uptime monitoring (UptimeRobot, Pingdom, etc.)
- Configure log aggregation (Papertrail, Loggly, etc.)

## Troubleshooting

### Application Won't Start

```bash
# Check logs
# Docker:
docker-compose logs web

# Heroku:
heroku logs --tail

# Manual:
sudo journalctl -u project-management -f

# Common issues:
# - Missing SECRET_KEY environment variable
# - Database connection failed
# - Port already in use
# - Missing dependencies
```

### Database Errors

```bash
# Reinitialize database
python -c "from app import create_app, db; app=create_app(); app.app_context().push(); db.drop_all(); db.create_all()"

# Check database URL
echo $DATABASE_URL

# Test connection
python -c "from app import create_app, db; app=create_app(); app.app_context().push(); print('Connected!')"
```

### 502 Bad Gateway

- Check if application is running: `sudo systemctl status project-management`
- Check Nginx configuration: `sudo nginx -t`
- Check application logs for errors
- Verify port binding matches Nginx proxy_pass

### Memory Issues

- Reduce number of Gunicorn workers
- Enable Redis caching to reduce database load
- Upgrade to higher tier plan
- Optimize database queries

### Slow Performance

- Enable Redis caching
- Add database indexes
- Upgrade to higher tier
- Use CDN for static files
- Enable Gzip compression

## Security Checklist

- [ ] Changed default `SECRET_KEY`
- [ ] Using HTTPS
- [ ] Database credentials secured
- [ ] Debug mode disabled (`FLASK_ENV=production`)
- [ ] Firewall configured (if VPS)
- [ ] Regular backups enabled
- [ ] Security headers enabled
- [ ] Rate limiting configured
- [ ] Dependencies up to date

## Maintenance

### Regular Updates

```bash
# Pull latest code
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart application
# Docker:
docker-compose restart web

# Heroku:
git push heroku main

# Manual:
sudo systemctl restart project-management
```

### Database Backups

```bash
# Manual backup
python scripts/backup_database.py

# Automated backups (add to crontab)
0 2 * * * cd /opt/project-management && /opt/project-management/venv/bin/python scripts/backup_database.py
```

## Support

For deployment issues:

1. Check the [GitHub Issues](https://github.com/xploitoverload/project-management/issues)
2. Review platform-specific documentation
3. Open a new issue with deployment logs

---

**Last Updated**: February 2026
**Version**: 2.0.0
