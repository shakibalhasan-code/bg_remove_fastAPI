#!/bin/bash
# Quick update script - run this when you push changes to GitHub
# Usage: ./update.sh

set -e

APP_DIR="/var/www/bg_remove"
SERVICE_NAME="bg-remover-api"

echo "🔄 Updating Background Remover API..."

cd $APP_DIR

echo "📥 Pulling latest changes from GitHub..."
git pull origin master

echo "🐍 Updating dependencies..."
source venv/bin/activate
pip install -r requirements.txt --upgrade

echo "🔄 Restarting service..."
sudo systemctl restart $SERVICE_NAME

echo "✅ Update complete!"
echo ""
echo "📊 Service Status:"
sudo systemctl status $SERVICE_NAME --no-pager -l

echo ""
echo "📝 View logs: sudo journalctl -u $SERVICE_NAME -f"
