# Multi-App Deployment Guide

This guide shows how to run multiple APIs on the same VPS, each in its own directory.

## 📁 Directory Structure

```
/var/www/
├── bg_remove/          # Background removal API (port 8000)
├── image_resize/       # Image resize API (port 8001)
├── pdf_converter/      # PDF converter API (port 8002)
└── ...                 # More apps
```

## 🚀 Deploy First App (bg_remove)

```bash
# SSH to VPS
ssh root@YOUR_VPS_IP

# Download and customize deploy script
wget https://raw.githubusercontent.com/shakibalhasan-code/bg_remove_fastAPI/master/deploy.sh
chmod +x deploy.sh

# Deploy (script will create /var/www/bg_remove/)
./deploy.sh
```

**Result**: API running at:
- `http://YOUR_VPS_IP/bg_remove/`
- `http://YOUR_VPS_IP:8000/`

## 🔄 Deploy Second App (Different Project)

```bash
# Clone your second project
cd /var/www
git clone https://github.com/YOUR_USERNAME/another_api.git another_project

# Copy deploy script from bg_remove
cp /var/www/bg_remove/deploy.sh /var/www/another_project/

# Edit configuration
cd /var/www/another_project
nano deploy.sh
```

**Change these lines in deploy.sh:**
```bash
APP_NAME="another_project"  # Change app name
NGINX_PORT="8001"          # Change port (8001, 8002, etc.)
REPO_URL="https://github.com/YOUR_USERNAME/another_api.git"
```

**Run deployment:**
```bash
./deploy.sh
```

**Result**: Second API running at:
- `http://YOUR_VPS_IP/another_project/`
- `http://YOUR_VPS_IP:8001/`

## 🌐 Access Patterns

### Pattern 1: Path-Based Access (Default)

All apps accessible under different paths on same domain:

```
http://YOUR_VPS_IP/bg_remove/         → Background Removal API
http://YOUR_VPS_IP/bg_remove/docs     → API Docs
http://YOUR_VPS_IP/bg_remove/health   → Health Check

http://YOUR_VPS_IP/another_project/   → Another API
http://YOUR_VPS_IP/another_project/docs
```

**Benefits:**
- ✅ One domain for all apps
- ✅ Easy to organize
- ✅ No DNS configuration needed

### Pattern 2: Subdomain Access

Each app gets its own subdomain:

```
http://bg-remove.yourdomain.com/      → Background Removal API
http://another.yourdomain.com/        → Another API
```

**Setup:**
1. Configure DNS A records for each subdomain
2. Enable standalone nginx config:
```bash
sudo ln -sf /etc/nginx/sites-available/bg_remove-api-standalone /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

### Pattern 3: Direct Port Access

Access apps directly via port:

```
http://YOUR_VPS_IP:8000/  → bg_remove
http://YOUR_VPS_IP:8001/  → another_project
```

**Note**: Need to open ports in firewall:
```bash
sudo ufw allow 8000
sudo ufw allow 8001
```

## 📋 Port Allocation Strategy

| App Name | Port | Service Name | Path |
|----------|------|-------------|------|
| bg_remove | 8000 | bg_remove-api | /bg_remove/ |
| image_resize | 8001 | image_resize-api | /image_resize/ |
| pdf_converter | 8002 | pdf_converter-api | /pdf_converter/ |
| text_ocr | 8003 | text_ocr-api | /text_ocr/ |

## 🔧 Managing Multiple Apps

### Check Status of All Apps

```bash
# List all services
sudo systemctl list-units | grep api

# Check specific app
sudo systemctl status bg_remove-api
sudo systemctl status another_project-api
```

### View Logs

```bash
# App 1
sudo journalctl -u bg_remove-api -f

# App 2
sudo journalctl -u another_project-api -f

# All apps together
sudo journalctl -f | grep api
```

### Restart Apps

```bash
# Restart specific app
sudo systemctl restart bg_remove-api

# Restart all apps
sudo systemctl restart bg_remove-api another_project-api

# Restart nginx (affects all)
sudo systemctl restart nginx
```

### Update Apps

```bash
# Update app 1
cd /var/www/bg_remove
./update.sh

# Update app 2
cd /var/www/another_project
./update.sh
```

## 🔒 Nginx Configuration

### Main Nginx Config (`/etc/nginx/sites-available/multi-api`)

For multiple apps, create one nginx config with all paths:

```nginx
# App 1: bg_remove
upstream bg_remove_backend {
    server 127.0.0.1:8000;
}

# App 2: another_project
upstream another_project_backend {
    server 127.0.0.1:8001;
}

server {
    listen 80;
    server_name your-domain.com;
    
    client_max_body_size 20M;
    
    # Background Removal API
    location /bg_remove/ {
        rewrite ^/bg_remove/(.*) /$1 break;
        proxy_pass http://bg_remove_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }
    
    # Another Project API
    location /another_project/ {
        rewrite ^/another_project/(.*) /$1 break;
        proxy_pass http://another_project_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }
}
```

## 💾 Resource Management

### Monitor Resource Usage

```bash
# CPU and Memory
htop

# Per-service resources
systemd-cgtop

# Disk usage
df -h
du -sh /var/www/*
```

### Adjust Workers Per App

Edit `gunicorn_conf.py` in each app directory:

```python
# Low-traffic app (fewer workers)
workers = 2

# High-traffic app (more workers)
workers = 8
```

### Set Resource Limits

Edit systemd service file:

```bash
sudo nano /etc/systemd/system/bg_remove-api.service
```

Add:
```ini
[Service]
# Limit memory to 1GB
MemoryMax=1G

# Limit CPU to 50%
CPUQuota=50%
```

Restart:
```bash
sudo systemctl daemon-reload
sudo systemctl restart bg_remove-api
```

## 🛡️ Firewall Configuration

```bash
# Allow HTTP/HTTPS
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 22  # SSH

# If using direct port access
sudo ufw allow 8000
sudo ufw allow 8001
sudo ufw allow 8002

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

## 🔐 SSL for Multiple Apps

### Option 1: Wildcard Certificate

```bash
# Get wildcard cert for *.yourdomain.com
sudo certbot certonly --manual --preferred-challenges dns -d "*.yourdomain.com" -d yourdomain.com
```

### Option 2: Individual Certificates

```bash
# Certificate per subdomain
sudo certbot --nginx -d bg-remove.yourdomain.com
sudo certbot --nginx -d another.yourdomain.com
```

### Option 3: Single Domain with Paths

```bash
# One cert for main domain
sudo certbot --nginx -d yourdomain.com
```

All paths (yourdomain.com/bg_remove/, etc.) use same certificate.

## 📊 Monitoring Setup

### Health Check All Apps

Create a monitoring script:

```bash
#!/bin/bash
# /usr/local/bin/check-apis.sh

echo "Checking all APIs..."

curl -s http://localhost:8000/health | jq '.'
curl -s http://localhost:8001/health | jq '.'
curl -s http://localhost:8002/health | jq '.'
```

Make executable:
```bash
chmod +x /usr/local/bin/check-apis.sh
```

### Automated Monitoring

Add to cron for alerts:
```bash
crontab -e
```

Add:
```
*/5 * * * * /usr/local/bin/check-apis.sh >> /var/log/api-health.log 2>&1
```

## 🚨 Troubleshooting Multiple Apps

### Port Already in Use

```bash
# Check what's using a port
sudo lsof -i :8000

# Kill process
sudo kill -9 <PID>
```

### Nginx Configuration Conflicts

```bash
# Test nginx config
sudo nginx -t

# Check enabled sites
ls -la /etc/nginx/sites-enabled/

# Disable conflicting site
sudo rm /etc/nginx/sites-enabled/default
```

### Apps Not Communicating

Check if services are running:
```bash
sudo systemctl status bg_remove-api
sudo systemctl status another_project-api
```

Check if ports are listening:
```bash
sudo netstat -tulpn | grep LISTEN
```

## 🎯 Best Practices

1. **Consistent Naming**: Use `app_name-api` pattern for services
2. **Port Management**: Document port assignments
3. **Resource Limits**: Set memory/CPU limits per app
4. **Separate Logs**: Each app logs to its own journal
5. **Independent Updates**: Each app can be updated separately
6. **Health Checks**: Implement for all apps
7. **Backup Strategy**: Backup each app directory separately

## 📝 Quick Reference

```bash
# Deploy new app
cd /var/www
git clone REPO_URL app_name
cd app_name
# Edit deploy.sh (change APP_NAME and NGINX_PORT)
./deploy.sh

# Update existing app
cd /var/www/app_name
./update.sh

# Check all services
sudo systemctl list-units | grep api

# Restart all
sudo systemctl restart bg_remove-api another_project-api nginx

# View all logs
sudo journalctl -f | grep api
```

## 🌟 Example: Complete 3-App Setup

```bash
# App 1: Background Remover (port 8000)
cd /var/www/bg_remove
# Access: http://YOUR_VPS_IP/bg_remove/

# App 2: Image Resizer (port 8001)
cd /var/www/image_resize
# Access: http://YOUR_VPS_IP/image_resize/

# App 3: PDF Converter (port 8002)
cd /var/www/pdf_converter
# Access: http://YOUR_VPS_IP/pdf_converter/
```

All running simultaneously, independently managed! 🎉
