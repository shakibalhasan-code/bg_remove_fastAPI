#!/bin/bash
# Deployment script for Hostinger Ubuntu VPS
# Run this script on your VPS server

set -e  # Exit on error

echo "🚀 Starting deployment of Background Remover API..."

# Configuration - Change APP_NAME for different projects
APP_NAME="bg_remove"  # Change this for different projects
APP_DIR="/var/www/$APP_NAME"
REPO_URL="https://github.com/shakibalhasan-code/bg_remove_fastAPI.git"
PYTHON_VERSION="python3.11"
SERVICE_NAME="$APP_NAME-api"
NGINX_PORT="8000"  # Change this for multiple projects (8000, 8001, 8002...)

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}📦 Step 1: Installing system dependencies...${NC}"
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev gcc g++ nginx git

echo -e "${BLUE}📂 Step 2: Setting up application directory...${NC}"
if [ -d "$APP_DIR" ]; then
    echo "Directory exists, pulling latest changes..."
    cd $APP_DIR
    git pull origin master
else
    echo "Cloning repository..."
    sudo mkdir -p $APP_DIR
    sudo chown $USER:$USER $APP_DIR
    git clone $REPO_URL $APP_DIR
    cd $APP_DIR
fi

echo -e "${BLUE}🐍 Step 3: Setting up Python virtual environment...${NC}"
if [ ! -d "venv" ]; then
    $PYTHON_VERSION -m venv venv
fi

source venv/bin/activate

echo -e "${BLUE}📚 Step 4: Installing Python dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

echo -e "${BLUE}⚙️  Step 5: Creating systemd service...${NC}"
sudo tee /etc/systemd/system/$SERVICE_NAME.service > /dev/null <<EOF
[Unit]
Description=Background Remover API
After=network.target

[Service]
Type=notify
User=$USER
Group=$USER
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"

ExecStart=$APP_DIR/venv/bin/gunicorn -c gunicorn_conf.py --bind 127.0.0.1:$NGINX_PORT main:app

Restart=always
RestartSec=10

LimitNOFILE=65536

StandardOutput=journal
StandardError=journal
SyslogIdentifier=$SERVICE_NAME

[Install]
WantedBy=multi-user.target
EOF

echo -e "${BLUE}🔧 Step 6: Configuring Nginx...${NC}"
sudo tee /etc/nginx/sites-available/$SERVICE_NAME > /dev/null <<EOF
upstream ${APP_NAME}_backend {
    server 127.0.0.1:$NGINX_PORT;
}

server {
    listen 80;
    server_name _;  # Accept all hostnames - update with your domain later
    
    # Root path for this API
    location /$APP_NAME/ {
    
    location / {
        proxy_pass http://${APP_NAME}_backend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
        
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    location /health {
        proxy_pass http://${APP_NAME}_backend/health;
        access_log off;
    }
}
EOF

echo ""
echo -e "${GREEN}📋 Nginx Configuration Options:${NC}"
echo "  1. Path-based: http://YOUR_VPS_IP/$APP_NAME/"
echo "  2. Standalone: http://${APP_NAME}.yourdomain.com (requires DNS setup)"

# Enable nginx site for path-based access/sites-available/${SERVICE_NAME}-standalone > /dev/null <<EOF
upstream ${APP_NAME}_backend {
    server 127.0.0.1:$NGINX_PORT;
}

server {
    listen 80;
    server_name ${APP_NAME}.yourdomain.com;  # Update with your subdomain
    
    client_max_body_size 20M;
    client_body_timeout 120s;
    
    location / {
        proxy_pass http://bg_remover_backend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
        
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    location /health {
        proxy_pass http://bg_remover_backend/health;
        access_log off;
    }
}
EOF

# Enable nginx site
sudo ln -sf /etc/nginx/sites-available/$SERVICE_NAME /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default  # Remove default site

# Test nginx configuration
sudo nginx -t

echo -e "${BLUE}🔥 Step 7: Starting services...${NC}"
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
sudo systemctl restart $SERVICE_NAME
sudo systemctl restart nginx

echo ""
echo -e "${GREEN}🎉 Your API is now running!${NC}"
echo ""
echo "📍 Access your API:"
echo "   Path-based: http://YOUR_VPS_IP/$APP_NAME/"
echo "   Direct port: http://YOUR_VPS_IP:$NGINX_PORT/"
echo ""
echo "📍 Test it:"
echo "   curl http://localhost:$NGINX_PORT/health"
echo "   curl http://YOUR_VPS_IP/$APP_NAME/health"
echo ""
echo "📚 API Documentation:"
echo "   http://YOUR_VPS_IP/$APP_NAME/docs"
echo ""
echo "📝 View logs:"
echo "   sudo journalctl -u $SERVICE_NAME -f"
echo ""
echo "🔄 Update deployment (run anytime):"
echo "   cd $APP_DIR && ./update.sh"
echo ""
echo "📦 Deployed to: $APP_DIR"
echo "🔧 Service name: $SERVICE_NAME"
echo "🌐 Port: $NGINX_PORT"
echo "📝 View logs:"
echo "   sudo journalctl -u $SERVICE_NAME -f"
echo ""
echo "🔄 Update deployment (run anytime):"
echo "   cd $APP_DIR && git pull && sudo systemctl restart $SERVICE_NAME"
