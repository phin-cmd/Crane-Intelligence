#!/bin/bash
# Ubuntu/DigitalOcean setup script for Crane Intelligence Platform
echo "🚀 Setting up Crane Intelligence Platform on Ubuntu..."

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
echo "🐍 Installing Python and dependencies..."
sudo apt install -y python3 python3-pip python3-venv python3-dev build-essential

# Install additional system dependencies
echo "📚 Installing additional dependencies..."
sudo apt install -y git curl wget unzip

# Create project directory (if not exists)
PROJECT_DIR="/opt/crane-intelligence"
if [ ! -d "$PROJECT_DIR" ]; then
    echo "📁 Creating project directory..."
    sudo mkdir -p $PROJECT_DIR
    sudo chown $USER:$USER $PROJECT_DIR
fi

# Copy project files (assuming you're running this from the project root)
echo "📋 Copying project files..."
cp -r . $PROJECT_DIR/
cd $PROJECT_DIR

# Create virtual environment
echo "🔧 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r backend/requirements.txt
pip install pandas numpy requests aiohttp beautifulsoup4 lxml pdfplumber openpyxl xlsxwriter

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs temp backups data

# Set permissions
echo "🔐 Setting permissions..."
chmod +x start_platform.sh
chmod +x deploy/cross_platform_deploy.py
chmod +x install_dependencies.py

# Create systemd service
echo "⚙️ Creating systemd service..."
sudo tee /etc/systemd/system/crane-intelligence.service > /dev/null <<EOF
[Unit]
Description=Crane Intelligence Platform
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_DIR
ExecStart=$PROJECT_DIR/start_platform.py
Restart=always
RestartSec=3
Environment=PATH=$PROJECT_DIR/venv/bin

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
echo "🚀 Enabling and starting service..."
sudo systemctl daemon-reload
sudo systemctl enable crane-intelligence
sudo systemctl start crane-intelligence

# Check status
echo "📊 Checking service status..."
sudo systemctl status crane-intelligence --no-pager

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📋 Service Management:"
echo "  Start:   sudo systemctl start crane-intelligence"
echo "  Stop:    sudo systemctl stop crane-intelligence"
echo "  Restart: sudo systemctl restart crane-intelligence"
echo "  Status:  sudo systemctl status crane-intelligence"
echo "  Logs:    sudo journalctl -u crane-intelligence -f"
echo ""
echo "🌐 Access URLs:"
echo "  Frontend: http://your-server-ip:3000/homepage.html"
echo "  Backend:  http://your-server-ip:8003"
echo "  API Docs: http://your-server-ip:8003/docs"
echo ""
echo "🔐 Demo Credentials:"
echo "  Email:    demo@craneintelligence.com"
echo "  Password: DemoOnly123"
