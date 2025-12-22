# Environment Parity Checklist

To ensure DEV and UAT work **exactly the same** as Production, the following items must match:

## ✅ Already Synchronized

### 1. **Application Code**
- ✅ Same codebase (all HTML, CSS, JS files)
- ✅ Same Docker images
- ✅ Same volume mappings
- ✅ Same file structure

### 2. **Database**
- ✅ Same schema (39 tables)
- ✅ Same data records
- ✅ Same table structures

### 3. **Docker Configuration**
- ✅ Same Dockerfile
- ✅ Same docker-compose structure
- ✅ Same service definitions
- ✅ Same volume mounts

## ⚠️ Items That MUST Match (Currently Different)

### 4. **Environment Variables** (Critical)

#### Must Match Production:
- `SECRET_KEY` - ✅ Already matching
- `BREVO_API_KEY` - ✅ Already matching  
- `BREVO_SMTP_PASSWORD` - ✅ Already matching
- `MAIL_FROM_EMAIL` - ✅ Already matching
- `MAIL_USERNAME` - ✅ Already matching
- `MAIL_SERVER` - ✅ Already matching
- `MAIL_PORT` - ✅ Already matching
- `USE_BREVO_API` - ✅ Already matching
- `MAIL_FROM_NAME` - ✅ Already matching
- `STRIPE_PUBLISHABLE_KEY` - ✅ Already matching
- `STRIPE_SECRET_KEY` - ✅ Already matching
- `GITHUB_TOKEN` - ✅ Already matching
- `DO_SPACES_KEY` - ✅ Already matching
- `DO_SPACES_SECRET` - ✅ Already matching
- `DO_SPACES_REGION` - ✅ Already matching
- `DO_SPACES_BUCKET` - ✅ Already matching
- `DO_SPACES_ENDPOINT` - ✅ Already matching
- `DO_SPACES_CDN_ENDPOINT` - ✅ Already matching

#### Should Be Different (Environment-Specific):
- `ENVIRONMENT` - dev/uat/production (correctly different)
- `FRONTEND_URL` - Different domains (correctly different)
- `API_URL` - Different domains (correctly different)
- `DATABASE_URL` - Different DB names (correctly different)
- `REDIS_URL` - Same within container (correctly same)

### 5. **Nginx Configuration**
- ✅ Same nginx.conf file
- ✅ Same routing rules
- ✅ Same proxy settings

### 6. **Static Assets**
- ✅ Same images/ directory
- ✅ Same css/ directory
- ✅ Same js/ directory
- ✅ Same components/ directory
- ✅ Same HTML files

### 7. **Backend Dependencies**
- ✅ Same requirements.txt
- ✅ Same Python packages
- ✅ Same Dockerfile for backend

### 8. **Frontend Configuration**
- ✅ Same NODE_ENV=production
- ✅ Same nginx configuration

## 🔍 Items to Verify

### 9. **File Permissions**
- Should be same across environments
- Check: `ls -la` on key files

### 10. **External Service Endpoints**
- Stripe API endpoints (should use same test/live keys)
- Brevo API endpoints (should use same)
- DigitalOcean Spaces endpoints (should use same bucket or separate)

### 11. **SSL Certificates**
- Different domains = different certificates (expected)
- But same certificate provider and configuration

### 12. **Logging Configuration**
- Should have same log levels
- Same log formats

### 13. **Error Handling**
- Same error pages
- Same error responses

## 📋 Complete Checklist

### Code & Configuration
- [x] Application code (HTML, CSS, JS)
- [x] Docker configuration
- [x] Nginx configuration
- [x] Environment variables (except URLs and DB names)
- [x] Static assets (images, CSS, JS)
- [x] Backend dependencies
- [x] Frontend dependencies

### Data & Database
- [x] Database schema
- [x] Database records
- [x] Database indexes
- [x] Database constraints

### Services & Integrations
- [x] Email service configuration (Brevo)
- [x] Payment service configuration (Stripe)
- [x] Storage service configuration (DO Spaces)
- [x] GitHub integration (if used)

### Infrastructure
- [x] Docker images
- [x] Container configurations
- [x] Volume mappings
- [x] Port mappings (internal)
- [x] Network configuration

### Security
- [x] Secret keys
- [x] API keys
- [x] Authentication configuration
- [x] CORS settings

## ⚠️ Items That SHOULD Be Different

These are intentionally different and should remain so:

1. **Domain Names**
   - Production: `craneintelligence.tech`
   - DEV: `dev.craneintelligence.tech`
   - UAT: `uat.craneintelligence.tech`

2. **Database Names**
   - Production: `crane_intelligence`
   - DEV: `crane_intelligence_dev`
   - UAT: `crane_intelligence_uat`

3. **Database Users**
   - Production: `crane_user`
   - DEV: `crane_dev_user`
   - UAT: `crane_uat_user`

4. **Environment Identifier**
   - Production: `production` (or not set)
   - DEV: `dev`
   - UAT: `uat`

5. **Application URLs**
   - Different `FRONTEND_URL` and `API_URL` per environment

6. **Port Mappings** (for local access)
   - Production: 3001, 8004, 5434, 6380, 8082
   - DEV: 3101, 8104, 5534, 6480, 8182
   - UAT: 3201, 8204, 5634, 6580, 8282

## 🎯 Summary

**To work exactly the same as production, DEV and UAT need:**

1. ✅ **Same code** - Already done
2. ✅ **Same database schema and data** - Already done
3. ✅ **Same environment variables** (except URLs/DB names) - Already done
4. ✅ **Same configuration files** - Already done
5. ✅ **Same static assets** - Already done
6. ✅ **Same Docker setup** - Already done
7. ✅ **Same dependencies** - Already done

**The only differences should be:**
- Domain names (URLs)
- Database names and users
- Environment identifier
- Port mappings (for local access)

All other configuration, code, data, and services should be identical!

