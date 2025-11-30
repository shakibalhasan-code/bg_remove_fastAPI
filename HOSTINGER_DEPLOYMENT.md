# Hostinger Ubuntu VPS Deployment Guide

## 📋 Prerequisites

- Ubuntu VPS from Hostinger (2GB+ RAM recommended)
- SSH access to your VPS
- Your GitHub repository is public or you have SSH keys set up

## 🚀 One-Command Deployment

### Step 1: Connect to Your VPS

```bash
ssh root@YOUR_VPS_IP
# or
ssh your-username@YOUR_VPS_IP
```

### Step 2: Download and Run Deployment Script

```bash
# Download deployment script
wget https://raw.githubusercontent.com/shakibalhasan-code/bg_remove_fastAPI/master/deploy.sh

# Make it executable
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

**That's it!** The script will:
1. ✅ Install Python 3.11, Nginx, and dependencies
2. ✅ Clone your repository
3. ✅ Set up virtual environment
4. ✅ Install Python packages
5. ✅ Configure systemd service
6. ✅ Configure Nginx reverse proxy
7. ✅ Start the API

---

## 🧪 Test Your API

After deployment completes:

```bash
# Test locally on VPS
curl http://localhost:8000/health

# Test from your computer (replace with your VPS IP)
curl http://YOUR_VPS_IP/health
```

**Visit in browser:**
- API Docs: `http://YOUR_VPS_IP/docs`
- Health Check: `http://YOUR_VPS_IP/health`

---

## 🔄 Update Your API (When You Push Changes)

Whenever you push changes to GitHub:

```bash
# SSH into your VPS
ssh root@YOUR_VPS_IP

# Run update script
cd /var/www/bg_remove
./update.sh
```

Or manually:
```bash
cd /var/www/bg_remove
git pull origin master
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart bg-remover-api
```

---

## 🔧 Useful Commands

### Check API Status
```bash
sudo systemctl status bg-remover-api
```

### View Logs (Real-time)
```bash
sudo journalctl -u bg-remover-api -f
```

### View Last 100 Log Lines
```bash
sudo journalctl -u bg-remover-api -n 100
```

### Restart API
```bash
sudo systemctl restart bg-remover-api
```

### Stop API
```bash
sudo systemctl stop bg-remover-api
```

### Start API
```bash
sudo systemctl start bg-remover-api
```

### Check Nginx Status
```bash
sudo systemctl status nginx
```

### View Nginx Logs
```bash
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

---

## 🌐 Add Your Domain (Optional)

### Step 1: Point Domain to VPS

In your domain registrar (like Namecheap, GoDaddy), add an A record:
```
Type: A
Host: @ (or your-api subdomain)
Value: YOUR_VPS_IP
TTL: 300
```

### Step 2: Update Nginx Configuration

```bash
sudo nano /etc/nginx/sites-available/bg-remover-api
```

Change this line:
```nginx
server_name _;
```

To:
```nginx
server_name your-domain.com;
```

Save and restart:
```bash
sudo nginx -t
sudo systemctl restart nginx
```

### Step 3: Add SSL Certificate (HTTPS)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal is configured automatically
```

Now your API is available at: `https://your-domain.com`

---

## 🔒 Security Configuration

### 1. Update CORS Settings

Edit `/var/www/bg_remove/main.py`:

```python
ALLOWED_ORIGINS = ["https://your-frontend-domain.com"]
```

Then restart:
```bash
sudo systemctl restart bg-remover-api
```

### 2. Enable Firewall

```bash
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

### 3. Disable Root Login (Recommended)

```bash
sudo adduser deploy
sudo usermod -aG sudo deploy
```

Then edit SSH config:
```bash
sudo nano /etc/ssh/sshd_config
```

Change:
```
PermitRootLogin no
```

Restart SSH:
```bash
sudo systemctl restart ssh
```

---

## 📊 Performance Optimization

### Adjust Worker Count

Edit `/var/www/bg_remove/gunicorn_conf.py`:

```python
# For 2 CPU cores:
workers = 5  # (2 * 2) + 1

# For 4 CPU cores:
workers = 9  # (2 * 4) + 1
```

Restart:
```bash
sudo systemctl restart bg-remover-api
```

### Enable GPU (If Available)

```bash
cd /var/www/bg_remove
source venv/bin/activate
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
sudo systemctl restart bg-remover-api
```

### Add Swap Space (For Low RAM VPS)

```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

---

## 🐛 Troubleshooting

### API Not Starting

```bash
# Check service status
sudo systemctl status bg-remover-api

# Check logs for errors
sudo journalctl -u bg-remover-api -n 50

# Common issues:
# 1. Port already in use
sudo lsof -i :8000
sudo kill -9 <PID>

# 2. Permission issues
sudo chown -R $USER:$USER /var/www/bg_remove

# 3. Python dependencies missing
cd /var/www/bg_remove
source venv/bin/activate
pip install -r requirements.txt
```

### Nginx Not Working

```bash
# Test configuration
sudo nginx -t

# Check logs
sudo tail -f /var/log/nginx/error.log

# Restart nginx
sudo systemctl restart nginx
```

### Out of Memory

```bash
# Check memory usage
free -h

# Add swap space (see Performance Optimization section)

# Reduce workers in gunicorn_conf.py
nano /var/www/bg_remove/gunicorn_conf.py
# Set: workers = 2
```

### Models Downloading Slowly

First request will be slow (downloads ~176MB of AI models). Pre-download:

```bash
cd /var/www/bg_remove
source venv/bin/activate
python -c "from backgroundremover.bg import get_model; get_model('u2net')"
```

---

## 📞 Testing Your API

### From Command Line

```bash
# Health check
curl http://YOUR_VPS_IP/health

# Test background removal
curl -X POST "http://YOUR_VPS_IP/remove-background-simple" \
  -F "file=@test.jpg" \
  -o output.png
```

### From Python

```python
import requests

response = requests.post(
    "http://YOUR_VPS_IP/remove-background-simple",
    files={"file": open("test.jpg", "rb")}
)

with open("output.png", "wb") as f:
    f.write(response.content)
```

### From Browser

1. Open: `http://YOUR_VPS_IP/docs`
2. Click on "POST /remove-background-simple"
3. Click "Try it out"
4. Upload an image
5. Click "Execute"
6. Download the result

---

## 📦 Backup and Restore

### Backup Configuration

```bash
cd /var/www/bg_remove
tar -czf ~/bg_remove_backup.tar.gz main.py gunicorn_conf.py requirements.txt
```

### Restore from Backup

```bash
cd /var/www/bg_remove
tar -xzf ~/bg_remove_backup.tar.gz
sudo systemctl restart bg-remover-api
```

---

## 💡 Workflow

### Your Development Workflow:

1. **Develop locally** on your Windows machine
2. **Test** with `python main.py`
3. **Push to GitHub** when ready
4. **SSH to VPS** and run `./update.sh`
5. **Done!** Changes are live

### Continuous Deployment Example:

```bash
# On your local machine (Windows)
git add .
git commit -m "Updated feature"
git push origin master

# On your VPS (via SSH)
cd /var/www/bg_remove && ./update.sh
```

---

## 🎯 Quick Reference

| Task | Command |
|------|---------|
| Deploy | `./deploy.sh` |
| Update | `./update.sh` |
| Status | `sudo systemctl status bg-remover-api` |
| Logs | `sudo journalctl -u bg-remover-api -f` |
| Restart | `sudo systemctl restart bg-remover-api` |
| Health | `curl http://localhost:8000/health` |

---

## 🆘 Need Help?

1. **Check logs**: `sudo journalctl -u bg-remover-api -f`
2. **Check Nginx**: `sudo tail -f /var/log/nginx/error.log`
3. **Test locally**: `curl http://localhost:8000/health`
4. **Service status**: `sudo systemctl status bg-remover-api`

Your API should be running smoothly! 🚀
