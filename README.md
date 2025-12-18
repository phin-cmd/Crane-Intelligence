# Crane Intelligence Platform

Professional crane valuation and market intelligence platform with Bloomberg Terminal-quality analytics.

## 🏗️ Project Overview

Crane Intelligence is a comprehensive platform for crane equipment valuation, market analysis, and FMV (Fair Market Value) report generation. The platform combines real-time market data, AI-powered valuation algorithms, and professional reporting tools.

### Key Features

- **Professional Valuation Terminal** - Bloomberg-style interface for crane market analysis
- **FMV Report Generation** - Expert-prepared Fair Market Value reports ($999-$1,499)
- **Real-Time Market Data** - Live pricing feeds and market indices
- **User Dashboard** - Track valuations, reports, and subscriptions
- **Admin Panel** - Manage FMV reports, users, and system settings
- **Subscription System** - Tiered access (Starter, Professional, Enterprise)
- **Email Notifications** - Automated emails via Brevo API
- **Authentication System** - Secure user authentication and authorization

## 📁 Project Structure

```
Crane-Intelligence/
├── frontend/                    # Frontend web application
│   ├── homepage.html           # Landing page
│   ├── dashboard.html          # User dashboard
│   ├── valuation_terminal.html # Main valuation tool
│   ├── admin-fmv-reports.html  # Admin FMV reports management
│   ├── report-generation.html  # FMV report generation form
│   ├── my-reports.html         # User reports view
│   ├── login.html              # Authentication
│   ├── js/                     # JavaScript files
│   │   ├── unified-auth.js     # Authentication system
│   │   ├── api-client.js       # API communication
│   │   ├── valuation-terminal.js # Valuation logic
│   │   ├── notification-system.js # Notifications
│   │   └── ...                 # Other JS modules
│   ├── css/                    # Stylesheets
│   ├── images/                 # Image assets
│   └── data/                   # Data files
│       └── crane-database.json # Crane specifications database
├── fmv-api/                    # FMV API Server (Node.js)
│   ├── server.js               # Main server file
│   ├── package.json            # Node dependencies
│   ├── .env.example            # Environment variables template
│   └── data/                   # Database files (gitignored)
├── backend/                    # Python Backend (FastAPI)
│   ├── app/                    # Application code
│   │   └── main.py             # Main FastAPI app
│   ├── config/                 # Configuration
│   ├── migrations/             # Database migrations
│   ├── requirements.txt        # Python dependencies
│   └── run.py                  # Application runner
├── nginx/                      # Nginx configuration
│   └── craneintelligence.conf  # Site configuration
├── .gitignore                  # Git ignore rules
├── README.md                   # This file
└── DEPLOYMENT.md               # Deployment guide
```

## 🚀 Technology Stack

### Frontend
- **HTML5/CSS3** - Modern responsive design
- **JavaScript (ES6+)** - Client-side logic
- **WebSocket** - Real-time data updates
- **Stripe** - Payment processing

### Backend
- **Node.js** - FMV API server (port 3000)
- **Python/FastAPI** - Main API backend (port 8003)
- **Nginx** - Reverse proxy and static file serving

### Services
- **Brevo API** - Email notifications
- **Stripe API** - Payment processing
- **WebSocket** - Real-time market data

### Database
- **JSON files** - Lightweight data storage
  - FMV reports
  - User data
  - Subscription tracking
  - Usage metrics

## 🔧 Installation

### Prerequisites
- Node.js 16+ and npm
- Python 3.8+
- Nginx
- Git

### Clone Repository
```bash
git clone https://github.com/phin-cmd/Crane-Intelligence.git
cd Crane-Intelligence
```

### Frontend Setup
```bash
# No build step required - static files
# Deploy to /var/www/craneintelligence.tech/
```

### FMV API Setup
```bash
cd fmv-api
npm install
cp .env.example .env
# Edit .env with your API keys
node server.js
```

### Python Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your configuration
python run.py
```

### Nginx Configuration
```bash
sudo cp nginx/craneintelligence.conf /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/craneintelligence.conf /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 🔐 Environment Variables

### FMV API (.env)
```
STRIPE_SECRET_KEY=sk_test_...
BREVO_API_KEY=xkeysib-...
PORT=3000
```

### Python Backend (.env)
```
DATABASE_URL=postgresql://...
SECRET_KEY=your-secret-key
API_PORT=8003
```

## 📊 API Endpoints

### FMV API (Node.js - Port 3000)
- `POST /api/v1/fmv-reports/create-payment-intent` - Create payment intent
- `POST /api/v1/fmv-reports/confirm-payment` - Confirm payment
- `GET /api/v1/fmv-reports/user/:email` - Get user reports
- `GET /api/v1/admin/fmv-reports` - Get all reports (admin)
- `PUT /api/v1/admin/fmv-reports/:id` - Update report status
- `POST /api/v1/admin/fmv-reports/:id/upload-pdf` - Upload PDF report
- `POST /api/v1/admin/fmv-reports/:id/send-email` - Send report email

### Python Backend (FastAPI - Port 8003)
- `/api/v1/auth/*` - Authentication endpoints
- `/api/v1/subscriptions/*` - Subscription management
- `/api/v1/valuations/*` - Valuation endpoints
- `/api/v1/users/*` - User management

## 🎯 Key Features

### 1. Valuation Terminal
- Real-time market data display
- Multi-factor valuation algorithm
- Risk assessment and scoring
- Comparable sales analysis
- Export to PDF/Excel

### 2. FMV Reports
- Two tiers: Standard ($999) and Enhanced ($1,499)
- 24-48 hour delivery
- Expert analyst review
- Comprehensive market analysis
- Professional PDF reports

### 3. User Dashboard
- Track all valuations
- View FMV report status
- Manage subscriptions
- Download completed reports
- Usage analytics

### 4. Admin Panel
- Manage FMV reports
- Upload and send PDF reports
- Update report status
- View customer details
- Track payments

### 5. Subscription System
- **Starter**: 1 valuation/month ($999)
- **Professional**: Unlimited valuations ($2,499/month)
- **Enterprise**: Custom solutions ($4,999/month)

## 🧪 Testing

### Test Homepage
```bash
curl https://craneintelligence.tech/homepage.html
```

### Test API
```bash
# Get user reports
curl https://craneintelligence.tech/api/v1/fmv-reports/user/test@example.com

# Get admin reports
curl https://craneintelligence.tech/api/v1/admin/fmv-reports
```

## 📦 Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

### Quick Deploy
```bash
# Pull latest code
git pull origin main

# Restart services
sudo systemctl restart fmv-api
sudo systemctl restart crane-backend
sudo systemctl reload nginx
```

## 🔒 Security

- HTTPS enforced via Nginx
- Environment variables for sensitive data
- CORS configured for API endpoints
- Input validation on all forms
- Secure payment processing via Stripe
- Authentication tokens for API access

## 📝 License

Proprietary - All rights reserved

## 👥 Team

- **Development**: Crane Intelligence Team
- **Contact**: phin@accranes.com
- **Website**: https://craneintelligence.tech

## 🆘 Support

For technical support or questions:
- Email: support@craneintelligence.com
- Documentation: https://craneintelligence.tech/docs
- GitHub Issues: https://github.com/phin-cmd/Crane-Intelligence/issues

## 📈 Version History

### v1.0.0 (November 2025)
- Initial production release
- FMV report generation system
- User dashboard and admin panel
- Email notification system
- Subscription management
- Payment processing integration

---

**Built with ❤️ by the Crane Intelligence Team**
