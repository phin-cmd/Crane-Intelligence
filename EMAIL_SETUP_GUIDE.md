# 📧 Crane Intelligence Email System Setup Guide

## 🎯 **EMAIL SYSTEM OVERVIEW**

The Crane Intelligence platform now includes a comprehensive email system with the following features:

### **✅ Implemented Email Types**
1. **User Registration** - Welcome email + email verification
2. **Password Reset** - Secure password reset with 1-hour expiry
3. **Welcome Email** - Professional welcome message
4. **Consultation Confirmation** - User confirmation + admin notification
5. **Admin Notifications** - New user registrations and consultations
6. **Subscription Confirmation** - Premium subscription confirmations
7. **Report Generation** - Report ready notifications
8. **Alert Notifications** - System alerts and updates
9. **Admin Communications** - Internal admin messages

## 🔧 **SETUP INSTRUCTIONS**

### **Step 1: Configure Gmail App Password**

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate App Password**:
   - Go to Google Account Settings
   - Security → 2-Step Verification → App passwords
   - Generate a new app password for "Mail"
   - Copy the 16-character password

### **Step 2: Update Environment Variables**

Edit `/root/Crane-Intelligence/.env` and replace:
```bash
MAIL_PASSWORD=your-gmail-app-password-here
```
With your actual Gmail app password:
```bash
MAIL_PASSWORD=your-16-character-app-password
```

### **Step 3: Restart Services**
```bash
cd /root/Crane-Intelligence
docker-compose restart backend
```

## 📧 **EMAIL TEMPLATES**

All emails are professionally designed with:
- **Crane Intelligence branding**
- **Responsive HTML design**
- **Plain text fallback**
- **Security features**
- **Professional styling**

### **Email Features**
- ✅ **HTML + Text versions**
- ✅ **Professional branding**
- ✅ **Security tokens with expiry**
- ✅ **Mobile-responsive design**
- ✅ **Company contact information**

## 🚀 **TESTING THE EMAIL SYSTEM**

### **Test Email Endpoint**
```bash
# Test welcome email
curl -X POST "http://localhost:8004/api/v1/test-email?email=your-email@example.com&email_type=welcome"

# Test verification email
curl -X POST "http://localhost:8004/api/v1/test-email?email=your-email@example.com&email_type=verification"

# Test password reset email
curl -X POST "http://localhost:8004/api/v1/test-email?email=your-email@example.com&email_type=password_reset"

# Test consultation email
curl -X POST "http://localhost:8004/api/v1/test-email?email=your-email@example.com&email_type=consultation"
```

### **Test User Registration**
```bash
curl -X POST "http://localhost:8004/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "full_name": "Test User"
  }'
```

### **Test Consultation Submission**
```bash
curl -X POST "http://localhost:8004/api/v1/consultations" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "message": "Test consultation message"
  }'
```

## 📋 **EMAIL CONFIGURATION DETAILS**

### **Current Settings**
- **SMTP Server**: smtp.gmail.com
- **Port**: 587 (TLS)
- **From Email**: pgenerelly@craneintelligence.tech
- **Company**: Crane Intelligence
- **Website**: https://craneintelligence.tech
- **Support**: pgenerelly@craneintelligence.tech

### **Security Settings**
- **Email Verification**: Required (24 hours expiry)
- **Password Reset**: 1 hour expiry
- **Rate Limiting**: 3-5 emails per minute per user

## 🔒 **SECURITY FEATURES**

1. **Rate Limiting**: Prevents email spam
2. **Token Expiry**: Secure time-limited tokens
3. **Email Verification**: Required for account activation
4. **Password Reset**: Secure token-based reset
5. **Admin Notifications**: Immediate alerts for new activity

## 📊 **MONITORING EMAIL SYSTEM**

### **Check Email Logs**
```bash
cd /root/Crane-Intelligence
docker-compose logs backend | grep -i email
```

### **Test Email Service Status**
```bash
curl -s http://localhost:8004/api/v1/health
```

## 🎨 **EMAIL BRANDING**

All emails include:
- **Crane Intelligence logo and branding**
- **Professional color scheme**
- **Company contact information**
- **Website links**
- **Security notices**
- **Mobile-responsive design**

## 🚨 **TROUBLESHOOTING**

### **Common Issues**

1. **"Email service not available"**
   - Check if email dependencies are installed
   - Restart backend container

2. **"Failed to send email"**
   - Verify Gmail app password
   - Check SMTP settings
   - Ensure 2FA is enabled

3. **"Authentication failed"**
   - Use app password, not regular password
   - Check Gmail account settings

### **Debug Commands**
```bash
# Check email service status
curl -X POST "http://localhost:8004/api/v1/test-email?email=test@example.com&email_type=welcome"

# Check backend logs
docker-compose logs backend --tail=50

# Test SMTP connection
docker-compose exec backend python -c "from email_service import email_service; print('Email service loaded successfully')"
```

## ✅ **NEXT STEPS**

1. **Set up Gmail app password**
2. **Update .env file with real password**
3. **Restart backend service**
4. **Test email functionality**
5. **Monitor email delivery**

## 📞 **SUPPORT**

If you encounter issues:
1. Check the logs: `docker-compose logs backend`
2. Test email endpoint: `/api/v1/test-email`
3. Verify Gmail settings
4. Check network connectivity

---

**🎉 Your Crane Intelligence email system is ready to use!**
