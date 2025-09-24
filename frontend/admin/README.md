# Admin Panel Access Guide

## 🎯 **Working Admin Panel Access Points**

### **Primary Access:**
- **Admin Login**: http://localhost:3000/admin/login.html
- **Admin Dashboard**: http://localhost:3000/admin/index.html (redirects to login if not authenticated)
- **Simple Admin Panel**: http://localhost:3000/admin/simple.html (login overlay + dashboard)

### **Testing & Debug:**
- **Debug Page**: http://localhost:3000/admin/debug.html
- **Test Login**: http://localhost:3000/admin/test-login.html

## 🔐 **Admin Credentials**

- **Email**: admin@craneintelligence.com
- **Password**: AdminOnly123
- **Role**: admin
- **Subscription**: enterprise

## 🚀 **How to Access Admin Panel**

### **Method 1: Direct Login**
1. Go to: http://localhost:3000/admin/login.html
2. Enter admin credentials
3. Click "Sign In"
4. You'll be redirected to the admin dashboard

### **Method 2: Admin Dashboard (Auto-redirect)**
1. Go to: http://localhost:3000/admin/
2. If not authenticated, you'll be redirected to login
3. After login, you'll be redirected back to dashboard

### **Method 3: Simple Admin Panel**
1. Go to: http://localhost:3000/admin/simple.html
2. Login overlay will appear
3. Enter credentials and login
4. Admin panel will be revealed

## 📊 **Admin Panel Features**

### **Dashboard Statistics:**
- Total Users: 3
- Total Reports: 3,421
- Revenue: $45,680
- System Uptime: 99.9%

### **Navigation Sections:**
- **Dashboard**: Overview and statistics
- **Users**: User management
- **Cranes**: Crane listings management
- **Reports**: Report management
- **Settings**: System settings
- **Logs**: System logs

## 🔧 **Troubleshooting**

### **If Admin Panel Doesn't Load:**
1. Check if backend is running: http://localhost:8003/health
2. Check if frontend is running: http://localhost:3000/homepage.html
3. Use debug page: http://localhost:3000/admin/debug.html

### **If Login Fails:**
1. Verify admin user exists in database
2. Check backend logs for errors
3. Use test login page: http://localhost:3000/admin/test-login.html

### **If Redirected to Wrong Login:**
- Make sure you're using the admin login page, not the regular login
- Clear browser cache and localStorage
- Use the debug page to check token status

## 🛠 **Development Notes**

- Admin panel uses JWT tokens stored in localStorage
- Token validation happens on page load
- Automatic redirect to login if not authenticated
- Role-based access control (admin users only)
- Fallback to mock data if API calls fail

## 📱 **Browser Compatibility**

- Chrome/Edge: ✅ Full support
- Firefox: ✅ Full support
- Safari: ✅ Full support
- Mobile browsers: ✅ Responsive design

## 🔒 **Security Features**

- JWT token authentication
- Role-based access control
- Token validation on each request
- Automatic logout on token expiry
- Secure credential handling