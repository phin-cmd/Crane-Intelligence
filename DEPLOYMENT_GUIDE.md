# 🚀 Crane Intelligence Platform - Production Deployment Guide

## 📋 Prerequisites

### System Requirements
- **OS**: Linux (Ubuntu 20.04+), Windows 10+, or macOS 10.15+
- **RAM**: Minimum 4GB, Recommended 8GB+
- **Storage**: Minimum 20GB free space
- **CPU**: 2+ cores recommended

### Software Requirements
- **Docker**: 20.10+ (with Docker Compose)
- **Git**: 2.30+
- **Python**: 3.12+ (for local development)

## 🐳 Docker Deployment (Recommended)

### Quick Start
```bash
# Clone the repository
git clone <repository-url>
cd crane-intelligence-platform

# Run deployment script
./deploy.sh  # Linux/macOS
# OR
deploy.bat  # Windows
```

### Manual Deployment
```bash
# 1. Create environment file
cp env.production .env
# Edit .env with your production values

# 2. Start services
docker-compose up -d

# 3. Initialize database
docker-compose exec backend python init_equipment_db.py

# 4. Check health
curl http://localhost:8003/health
curl http://localhost:3000
```

## 🔧 Configuration

### Environment Variables
Update `.env` file with your production values:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/crane_intelligence

# Security
SECRET_KEY=your-super-secret-key-here

# Email
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# External APIs
EQUIPMENT_WATCH_API_KEY=your-api-key
```

### SSL Configuration
1. Place your SSL certificates in `ssl/` directory
2. Update `nginx.conf` with correct paths
3. Update environment variables

## 🌐 Access Points

After successful deployment:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8003
- **API Documentation**: http://localhost:8003/docs
- **Admin Portal**: http://localhost:3000/admin/dashboard.html

## 📊 Service Management

### Check Service Status
```bash
docker-compose ps
```

### View Logs
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs backend
docker-compose logs frontend
```

### Restart Services
```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart backend
```

### Update Services
```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## 🔒 Security Configuration

### Production Security Checklist
- [ ] Change default secret keys
- [ ] Configure SSL certificates
- [ ] Set up firewall rules
- [ ] Enable rate limiting
- [ ] Configure CORS properly
- [ ] Set up monitoring
- [ ] Enable logging
- [ ] Configure backups

### SSL Setup
1. Obtain SSL certificates from your CA
2. Place certificates in `ssl/` directory
3. Update nginx configuration
4. Restart services

## 📈 Monitoring & Maintenance

### Health Checks
```bash
# Check service health
curl http://localhost:8003/health
curl http://localhost:8003/api/v1/auth/health
curl http://localhost:8003/api/v1/valuation/health
```

### Database Backups
```bash
# Create backup
docker-compose exec db pg_dump -U crane_user crane_intelligence > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore backup
docker-compose exec -T db psql -U crane_user crane_intelligence < backup_file.sql
```

### Log Management
```bash
# View recent logs
docker-compose logs --tail=100

# Follow logs in real-time
docker-compose logs -f
```

## 🚨 Troubleshooting

### Common Issues

#### Services Not Starting
```bash
# Check logs
docker-compose logs

# Check resource usage
docker stats

# Restart services
docker-compose restart
```

#### Database Connection Issues
```bash
# Check database status
docker-compose exec db pg_isready

# Check database logs
docker-compose logs db
```

#### Frontend Not Loading
```bash
# Check nginx configuration
docker-compose exec nginx nginx -t

# Restart nginx
docker-compose restart nginx
```

### Performance Optimization

#### Resource Limits
Update `docker-compose.yml` with resource limits:
```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
```

#### Database Optimization
```sql
-- Create indexes for better performance
CREATE INDEX idx_crane_listings_make_model ON crane_listings(make, model);
CREATE INDEX idx_crane_listings_price ON crane_listings(price);
CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);
```

## 🔄 Updates & Maintenance

### Regular Maintenance Tasks
1. **Weekly**: Check service health and logs
2. **Monthly**: Update dependencies and security patches
3. **Quarterly**: Review and optimize database performance
4. **Annually**: Security audit and penetration testing

### Backup Strategy
- **Database**: Daily automated backups
- **Application Data**: Weekly backups
- **Configuration**: Version controlled
- **Logs**: Rotated weekly

## 📞 Support

For deployment issues or questions:
- Check logs: `docker-compose logs`
- Review documentation: `/docs` directory
- Contact support: support@craneintelligence.com

## 🎯 Production Checklist

Before going live:
- [ ] All environment variables configured
- [ ] SSL certificates installed
- [ ] Database initialized with demo data
- [ ] Health checks passing
- [ ] Monitoring configured
- [ ] Backup strategy implemented
- [ ] Security review completed
- [ ] Performance testing done
- [ ] Documentation updated
- [ ] Team training completed

