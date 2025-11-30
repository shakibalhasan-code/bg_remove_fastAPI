# Quick Start Deployment Checklist

## ✅ Pre-Deployment Checklist

- [ ] Python 3.10 or 3.11 installed on VPS
- [ ] Domain name pointed to VPS IP
- [ ] SSH access to VPS
- [ ] At least 2GB RAM available (4GB+ recommended)

## 🚀 Quick Deploy with Docker (5 minutes)

```bash
# 1. Install Docker (if not installed)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 2. Upload your code to VPS
scp -r * user@your-vps:/var/www/bg_remove/

# 3. SSH into VPS and deploy
ssh user@your-vps
cd /var/www/bg_remove
docker-compose up -d

# 4. Verify it's running
curl http://localhost:8000/health
```

**Done! API is now running on port 8000**

## 🔒 Add Nginx + SSL (10 minutes)

```bash
# 1. Install Nginx
sudo apt update
sudo apt install -y nginx certbot python3-certbot-nginx

# 2. Configure Nginx
sudo cp nginx.conf /etc/nginx/sites-available/bg-remover-api
sudo nano /etc/nginx/sites-available/bg-remover-api
# Change: server_name your-domain.com;

sudo ln -s /etc/nginx/sites-available/bg-remover-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# 3. Get SSL Certificate
sudo certbot --nginx -d your-domain.com

# 4. Test
curl https://your-domain.com/health
```

## ⚙️ Production Configuration

### Update CORS (Important!)

Edit `main.py`:
```python
ALLOWED_ORIGINS = ["https://your-frontend-domain.com"]
```

Rebuild:
```bash
docker-compose down
docker-compose up -d --build
```

## 📊 Monitoring Commands

```bash
# Check API logs
docker-compose logs -f

# Check API health
curl http://localhost:8000/health

# Check resource usage
docker stats

# Restart if needed
docker-compose restart
```

## 🔧 Common Issues

### Issue: Port 8000 already in use
```bash
sudo lsof -i :8000
sudo kill -9 <PID>
```

### Issue: Out of memory
```bash
# Add swap space
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Issue: Models downloading slowly
Models (~176MB) download on first request. Be patient or pre-download:
```bash
docker-compose exec bg-remover-api python -c "from backgroundremover.bg import get_model; get_model('u2net')"
```

## 🎯 Test Your API

```bash
# From your local machine
curl -X POST "https://your-domain.com/remove-background-simple" \
  -F "file=@test_image.jpg" \
  -o output.png

# Open output.png - background should be removed!
```

## 📱 API Endpoints

- `GET  /` - API info
- `GET  /health` - Health check
- `GET  /docs` - Interactive documentation
- `POST /remove-background-simple` - Quick background removal
- `POST /remove-background` - Advanced with options

## 🔐 Security Hardening

```bash
# 1. Enable firewall
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable

# 2. Update CORS in main.py (don't use "*" in production)
# 3. Enable rate limiting in nginx (see nginx.conf)
# 4. Regular updates
sudo apt update && sudo apt upgrade -y
```

## 💡 Tips

1. **Use GPU** for 5-10x faster processing (if available)
2. **Cache models** - first request will be slow
3. **Monitor resources** - background removal is CPU/GPU intensive
4. **Set file limits** - default is 10MB max
5. **Use CDN** - for high traffic, put Cloudflare in front

## 📞 Getting Help

Check logs:
```bash
docker-compose logs -f
```

Need more details? See `DEPLOYMENT.md`
