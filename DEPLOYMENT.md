# Production Deployment Guide

## Prerequisites

- VPS with Ubuntu 20.04+ (2GB RAM minimum, 4GB+ recommended)
- Python 3.10 or 3.11 installed
- Sudo access

## Option 1: Docker Deployment (Recommended)

### 1. Install Docker

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

Log out and back in for group changes to take effect.

### 2. Install Docker Compose

```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 3. Deploy the Application

```bash
# Clone or upload your code to the server
cd /var/www/bg_remove

# Build and start the container
docker-compose up -d

# Check logs
docker-compose logs -f

# Check status
docker-compose ps
```

### 4. Update CORS Settings

Edit `main.py` and update:
```python
ALLOWED_ORIGINS = ["https://yourdomain.com", "https://www.yourdomain.com"]
```

Rebuild:
```bash
docker-compose down
docker-compose up -d --build
```

## Option 2: Direct VPS Deployment

### 1. Install System Dependencies

```bash
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev gcc g++ nginx
```

### 2. Setup Application

```bash
# Create application directory
sudo mkdir -p /var/www/bg_remove
sudo chown $USER:$USER /var/www/bg_remove
cd /var/www/bg_remove

# Upload your code here

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn
```

### 3. Configure Gunicorn Service

```bash
# Copy systemd service file
sudo cp systemd.service /etc/systemd/system/bg-remover-api.service

# Edit the service file with your paths
sudo nano /etc/systemd/system/bg-remover-api.service

# Enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable bg-remover-api
sudo systemctl start bg-remover-api

# Check status
sudo systemctl status bg-remover-api

# View logs
sudo journalctl -u bg-remover-api -f
```

### 4. Configure Nginx

```bash
# Copy nginx configuration
sudo cp nginx.conf /etc/nginx/sites-available/bg-remover-api

# Edit with your domain
sudo nano /etc/nginx/sites-available/bg-remover-api

# Enable the site
sudo ln -s /etc/nginx/sites-available/bg-remover-api /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx
```

### 5. Setup SSL with Let's Encrypt (Recommended)

```bash
# Install certbot
sudo apt install -y certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal is configured automatically
# Test renewal
sudo certbot renew --dry-run
```

## Configuration for Production

### 1. Update CORS Settings

Edit `main.py`:
```python
ALLOWED_ORIGINS = ["https://yourdomain.com"]
```

### 2. Enable Trusted Host Middleware

Uncomment in `main.py`:
```python
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["yourdomain.com", "*.yourdomain.com"]
)
```

### 3. Adjust File Size Limits

In `main.py`:
```python
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB
```

In `nginx.conf`:
```nginx
client_max_body_size 20M;
```

### 4. Configure Workers

Based on your VPS CPU cores:
```python
# In gunicorn_conf.py
workers = (2 * CPU_CORES) + 1
```

## Monitoring

### Check API Health

```bash
curl http://localhost:8000/health
```

### Monitor Logs

```bash
# Docker
docker-compose logs -f

# Systemd
sudo journalctl -u bg-remover-api -f

# Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Resource Monitoring

```bash
# CPU and Memory
htop

# Docker stats
docker stats
```

## Performance Optimization

### 1. Enable GPU (if available)

Install CUDA and PyTorch with CUDA support:
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### 2. Caching Models

Models are automatically cached in `~/.u2net` or `/root/.u2net`

### 3. Load Balancing

For high traffic, use multiple instances behind a load balancer.

## Backup and Maintenance

### Backup Configuration

```bash
# Backup important files
tar -czf backup.tar.gz main.py gunicorn_conf.py nginx.conf requirements.txt
```

### Update Application

```bash
# Docker
docker-compose pull
docker-compose up -d

# Direct deployment
cd /var/www/bg_remove
source venv/bin/activate
git pull  # or upload new files
pip install -r requirements.txt
sudo systemctl restart bg-remover-api
```

## Troubleshooting

### API not responding

```bash
# Check service status
sudo systemctl status bg-remover-api

# Check logs
sudo journalctl -u bg-remover-api -n 100

# Restart service
sudo systemctl restart bg-remover-api
```

### High memory usage

- Reduce number of workers in `gunicorn_conf.py`
- Reduce `MAX_FILE_SIZE`
- Add swap space

### Slow processing

- Enable GPU support
- Use `u2netp` model (faster but lower quality)
- Increase timeout in nginx and gunicorn

## Security Checklist

- [ ] Configure firewall (UFW)
- [ ] Enable HTTPS with SSL certificate
- [ ] Set up rate limiting (nginx or application level)
- [ ] Configure CORS with specific domains
- [ ] Enable Trusted Host middleware
- [ ] Regular security updates
- [ ] Monitor logs for suspicious activity
- [ ] Use non-root user for application
- [ ] Secure sensitive environment variables

## Support

For issues, check:
1. Application logs: `sudo journalctl -u bg-remover-api`
2. Nginx logs: `/var/log/nginx/error.log`
3. API health: `curl http://localhost:8000/health`
