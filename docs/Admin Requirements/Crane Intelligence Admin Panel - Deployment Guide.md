# Crane Intelligence Admin Panel - Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying the comprehensive Crane Intelligence Admin Panel, a Bloomberg Terminal-style administrative interface for complete platform management.

## Package Contents

The `Crane_Intelligence_Admin_Panel_Complete.zip` package includes:

### Core Application
- **Backend API**: FastAPI-based REST API with admin endpoints
- **Database Models**: SQLAlchemy models for all platform entities
- **Authentication**: JWT-based security with role-based access control
- **Configuration**: Environment-based configuration management

### Admin Panel Interface
- **HTML Template**: `admin/templates/admin.html` - Complete admin interface
- **CSS Styles**: `static/css/admin.css` - Bloomberg Terminal-inspired styling
- **JavaScript**: `static/js/admin.js` - Interactive functionality and charts
- **Documentation**: `admin/README.md` - Comprehensive feature documentation

### Platform Integration
- **User Interface**: Existing homepage, dashboard, and valuation pages
- **Database**: Pre-configured SQLite database with sample data
- **Static Assets**: CSS frameworks and JavaScript libraries

## System Requirements

### Minimum Requirements
- **Operating System**: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 18.04+)
- **Python**: Version 3.8 or higher
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Storage**: 2GB available disk space
- **Network**: Internet connection for external data sources

### Recommended Requirements
- **CPU**: Multi-core processor (4+ cores)
- **Memory**: 16GB RAM for optimal performance
- **Storage**: SSD with 10GB available space
- **Network**: High-speed internet for real-time data updates

## Installation Steps

### 1. Extract Package
```bash
# Extract the complete package
unzip Crane_Intelligence_Admin_Panel_Complete.zip
cd "Crane Intelligence"
```

### 2. Set Up Python Environment
```bash
# Create virtual environment (recommended)
python -m venv crane_intelligence_env

# Activate virtual environment
# On Windows:
crane_intelligence_env\Scripts\activate
# On macOS/Linux:
source crane_intelligence_env/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
# Copy environment template (if provided)
cp .env.example .env

# Edit configuration file
# Set database URL, secret keys, and API endpoints
```

### 4. Initialize Database
```bash
# The package includes a pre-configured database
# For fresh installation, run:
python -c "from app.core.database import create_tables; create_tables()"
```

### 5. Start the Application
```bash
# Start the FastAPI server
python main.py

# Alternative using uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## Access Points

### Admin Panel
- **URL**: `http://localhost:8000/admin`
- **Default Credentials**: 
  - Username: `admin@craneintelligence.com`
  - Password: `admin123` (change immediately)

### User Interface
- **Homepage**: `http://localhost:8000/`
- **Dashboard**: `http://localhost:8000/dashboard`
- **Valuation**: `http://localhost:8000/valuation`

### API Documentation
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Admin Panel Features

### 🎛️ Dashboard Overview
- **Real-time Metrics**: Live platform statistics
- **System Health**: Performance monitoring
- **Quick Actions**: Common administrative tasks
- **Activity Feed**: Recent platform events

### 👥 User Management
- **User Directory**: Complete user listing with search/filter
- **Role Management**: Hierarchical permission system
- **Bulk Operations**: Mass user actions
- **Account Controls**: Creation, editing, suspension

### 📝 Content Management
- **Content Library**: Centralized content organization
- **Media Management**: File upload and organization
- **Template System**: Customizable content templates
- **Publishing Workflow**: Content approval process

### 📊 Analytics & Reporting
- **Performance Analytics**: Platform usage metrics
- **User Behavior**: Detailed journey tracking
- **Financial Reports**: Revenue and subscription analytics
- **Technical Metrics**: System performance data

### ⚙️ Platform Configuration
- **General Settings**: Platform information and configuration
- **API Management**: Rate limiting and integration controls
- **Email Configuration**: SMTP and notification templates
- **Billing Setup**: Payment processing and subscription plans

### 🔒 Security & Access Control
- **Role-based Access**: Granular permission management
- **Authentication Controls**: 2FA, password policies
- **IP Management**: Whitelist and access controls
- **Security Monitoring**: Threat detection and audit trails

### 🗄️ Data Management
- **Data Sources**: External API integration
- **Quality Control**: Data validation and cleanup
- **Processing Jobs**: Background task management
- **Database Tools**: Performance optimization

## Configuration Options

### Environment Variables
```bash
# Database Configuration
DATABASE_URL=sqlite:///./crane_intelligence.db

# Security Settings
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# External API Keys
EQUIPMENT_WATCH_API_KEY=your-api-key
RITCHIE_BROS_API_KEY=your-api-key

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@domain.com
SMTP_PASSWORD=your-app-password
```

### Admin Panel Customization
```css
/* Custom theme variables in admin.css */
:root {
    --primary-color: #00FF85;
    --dark-bg: #1A1A1A;
    --dark-bg-secondary: #2A2A2A;
    --text-color: #E0E0E0;
    --border-color: #444;
}
```

## Security Setup

### 1. Change Default Credentials
```python
# Create new admin user
from app.models.user import User
from app.core.security import get_password_hash

# Update admin password
admin_user = session.query(User).filter(User.email == "admin@craneintelligence.com").first()
admin_user.hashed_password = get_password_hash("new_secure_password")
session.commit()
```

### 2. Configure HTTPS
```bash
# For production deployment, use reverse proxy (nginx/Apache)
# Or configure SSL certificates directly in uvicorn
uvicorn main:app --host 0.0.0.0 --port 443 --ssl-keyfile=key.pem --ssl-certfile=cert.pem
```

### 3. Set Up Firewall Rules
```bash
# Allow only necessary ports
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

## Production Deployment

### Using Docker (Recommended)
```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# Build and run
docker build -t crane-intelligence-admin .
docker run -p 8000:8000 crane-intelligence-admin
```

### Using systemd (Linux)
```ini
# /etc/systemd/system/crane-intelligence.service
[Unit]
Description=Crane Intelligence Admin Panel
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/crane-intelligence
Environment=PATH=/opt/crane-intelligence/venv/bin
ExecStart=/opt/crane-intelligence/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

### Reverse Proxy (nginx)
```nginx
# /etc/nginx/sites-available/crane-intelligence
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
}
```

## Monitoring & Maintenance

### Health Checks
```bash
# Check application status
curl http://localhost:8000/health

# Monitor system resources
htop
df -h
```

### Log Management
```bash
# View application logs
tail -f logs/crane_intelligence.log

# Rotate logs (configure logrotate)
sudo logrotate /etc/logrotate.d/crane-intelligence
```

### Database Maintenance
```python
# Regular maintenance tasks
from app.core.database import engine
from sqlalchemy import text

# Analyze database performance
with engine.connect() as conn:
    result = conn.execute(text("ANALYZE"))
    
# Vacuum database (SQLite)
with engine.connect() as conn:
    conn.execute(text("VACUUM"))
```

## Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000
# Kill process if necessary
kill -9 <PID>
```

#### Database Connection Errors
```bash
# Check database file permissions
ls -la crane_intelligence.db
# Ensure write permissions for application user
chmod 664 crane_intelligence.db
```

#### Static Files Not Loading
```bash
# Verify static file paths in main.py
# Ensure static directory exists and has proper permissions
ls -la static/
```

### Performance Optimization

#### Database Optimization
```sql
-- Create indexes for frequently queried columns
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_cranes_model ON cranes(model);
CREATE INDEX idx_valuations_date ON valuations(created_at);
```

#### Caching Configuration
```python
# Add Redis caching for improved performance
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

FastAPICache.init(RedisBackend(), prefix="crane-intelligence")
```

## Support & Updates

### Getting Help
- **Documentation**: Refer to `admin/README.md` for detailed feature documentation
- **API Reference**: Access Swagger UI at `/docs` for API documentation
- **Logs**: Check application logs for error details
- **Community**: Join the Crane Intelligence community forums

### Updating the System
```bash
# Backup current installation
cp -r "Crane Intelligence" "Crane Intelligence_backup_$(date +%Y%m%d)"

# Apply updates
git pull origin main  # If using git
# Or extract new package version

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart application
sudo systemctl restart crane-intelligence
```

### Version Information
- **Admin Panel Version**: 1.0.0
- **API Version**: v1
- **Database Schema**: Latest
- **Last Updated**: September 2025

---

For technical support or questions about deployment, please refer to the comprehensive documentation or contact the development team.
