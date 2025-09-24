# 🚀 Crane Intelligence Platform - Cloud Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying the Crane Intelligence Platform to cloud infrastructure with enterprise-grade security, monitoring, and scalability.

## 📋 Prerequisites

- Cloud provider account (DigitalOcean, AWS, Google Cloud, or Azure)
- Domain name (optional but recommended)
- SSH key pair
- Basic knowledge of Linux commands

## 🎯 Recommended Infrastructure

### **Minimum Requirements**
- **CPU**: 2 vCPUs
- **RAM**: 4GB
- **Storage**: 80GB SSD
- **OS**: Ubuntu 22.04 LTS
- **Database**: PostgreSQL 14+
- **Cache**: Redis 6+

### **Recommended Configuration**
- **CPU**: 4 vCPUs
- **RAM**: 8GB
- **Storage**: 160GB SSD
- **Backups**: Enabled
- **Monitoring**: Enabled

## 🚀 Quick Deployment

### **Option 1: Automated Deployment (Recommended)**

1. **Upload deployment files to your server:**
   ```bash
   scp production-deployment.sh root@your-server-ip:/root/
   scp production-config.py root@your-server-ip:/root/
   ```

2. **Run the deployment script:**
   ```bash
   ssh root@your-server-ip
   chmod +x production-deployment.sh
   export DOMAIN_NAME="your-domain.com"
   ./production-deployment.sh
   ```

### **Option 2: Manual Deployment**

1. **Update system:**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Install dependencies:**
   ```bash
   sudo apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib redis-server nginx certbot python3-certbot-nginx ufw fail2ban
   ```

3. **Configure database:**
   ```bash
   sudo -u postgres psql
   CREATE DATABASE crane_intelligence_prod;
   CREATE USER crane_app WITH PASSWORD 'secure_password';
   GRANT ALL PRIVILEGES ON DATABASE crane_intelligence_prod TO crane_app;
   \q
   ```

4. **Deploy application:**
   ```bash
   mkdir -p /opt/crane-intelligence
   cp -r . /opt/crane-intelligence/
   cd /opt/crane-intelligence
   python3 -m venv venv
   source venv/bin/activate
   pip install -r backend/requirements.txt
   ```

## 🔧 Configuration

### **Environment Variables**

Create `/opt/crane-intelligence/.env`:
```bash
# Database
DATABASE_URL=postgresql://crane_app:password@localhost:5432/crane_intelligence_prod

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-super-secret-key
JWT_SECRET_KEY=your-jwt-secret-key

# Email
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Domain
DOMAIN_NAME=your-domain.com
```

### **Nginx Configuration**

The deployment script automatically configures Nginx with:
- SSL termination
- Rate limiting
- Security headers
- Static file serving
- Reverse proxy to application

### **Systemd Service**

The deployment script creates a systemd service for:
- Automatic startup
- Process management
- Logging
- Restart on failure

## 🔒 Security Features

### **Network Security**
- ✅ UFW firewall with strict rules
- ✅ Fail2Ban protection
- ✅ Rate limiting
- ✅ DDoS protection

### **Application Security**
- ✅ HTTPS encryption
- ✅ Security headers
- ✅ Input validation
- ✅ JWT authentication
- ✅ Password hashing

### **System Security**
- ✅ SSH hardening
- ✅ Service isolation
- ✅ Log monitoring
- ✅ Automated updates

## 📊 Monitoring & Maintenance

### **Health Checks**
- Automated health checks every 5 minutes
- Database connection monitoring
- Redis connection monitoring
- Resource usage monitoring

### **Backups**
- Daily automated backups
- Database backups
- Application backups
- 30-day retention

### **Log Management**
- Centralized logging
- Log rotation
- Error tracking
- Performance monitoring

## 🚨 Troubleshooting

### **Common Issues**

1. **Service not starting:**
   ```bash
   sudo systemctl status crane-intelligence
   sudo journalctl -u crane-intelligence -f
   ```

2. **Database connection issues:**
   ```bash
   sudo systemctl status postgresql
   sudo -u postgres psql -c "SELECT 1;"
   ```

3. **Nginx issues:**
   ```bash
   sudo nginx -t
   sudo systemctl status nginx
   ```

4. **High resource usage:**
   ```bash
   htop
   df -h
   free -h
   ```

### **Log Files**
- **Application**: `/opt/crane-intelligence/logs/app.log`
- **Nginx**: `/var/log/nginx/access.log`, `/var/log/nginx/error.log`
- **System**: `/var/log/syslog`
- **Security**: `/var/log/auth.log`

## 📈 Performance Optimization

### **Database Optimization**
- Connection pooling
- Query optimization
- Index optimization
- Regular VACUUM and ANALYZE

### **Caching**
- Redis caching
- Static file caching
- API response caching
- Database query caching

### **Load Balancing**
- Multiple application instances
- Database replication
- CDN integration
- Horizontal scaling

## 🔄 Updates & Maintenance

### **Application Updates**
```bash
cd /opt/crane-intelligence
git pull origin main
source venv/bin/activate
pip install -r backend/requirements.txt
sudo systemctl restart crane-intelligence
```

### **Security Updates**
```bash
sudo apt update && sudo apt upgrade -y
sudo systemctl restart crane-intelligence
```

### **Database Maintenance**
```bash
sudo -u postgres psql -d crane_intelligence_prod -c "VACUUM ANALYZE;"
```

## 📞 Support

### **Monitoring Commands**
- **Status**: `sudo systemctl status crane-intelligence`
- **Logs**: `sudo journalctl -u crane-intelligence -f`
- **Health**: `/opt/crane-intelligence/monitor.sh`
- **Backup**: `/opt/crane-intelligence/backup.sh`

### **Emergency Procedures**
- **Restart**: `sudo systemctl restart crane-intelligence`
- **Stop**: `sudo systemctl stop crane-intelligence`
- **Start**: `sudo systemctl start crane-intelligence`

## 🎯 Post-Deployment Checklist

- [ ] Application accessible via domain
- [ ] SSL certificate installed
- [ ] Health checks passing
- [ ] Monitoring dashboards active
- [ ] Backup strategy working
- [ ] Security scan completed
- [ ] Performance benchmarks met
- [ ] User accounts created
- [ ] Documentation updated

## 🚀 Launch Preparation

### **Pre-Launch**
1. Complete security scan
2. Run load tests
3. Verify all features
4. Test backup/restore
5. Configure monitoring alerts

### **Launch Day**
1. Monitor system metrics
2. Watch for errors
3. Collect user feedback
4. Document issues
5. Plan improvements

---

## 🎉 Congratulations!

Your Crane Intelligence platform is now deployed with enterprise-grade security, monitoring, and scalability. The system is ready for production use with comprehensive testing, monitoring, and security measures in place.

**Next Steps:**
1. Configure your domain DNS
2. Install SSL certificate
3. Create user accounts
4. Monitor system performance
5. Collect user feedback
6. Iterate and improve

**Support:** For any issues, check the monitoring dashboards and log files. The system includes comprehensive monitoring and alerting to help you maintain optimal performance.
