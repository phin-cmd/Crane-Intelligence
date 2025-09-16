# 🚀 Crane Intelligence Platform v2.0

**Professional Crane Valuation and Market Analysis Platform**

## 📁 **Project Structure**

```
crane-intelligence-platform/
├── backend/                    # FastAPI backend application
│   ├── app/                   # Main application code
│   │   ├── api/v1/           # API endpoints
│   │   ├── core/             # Configuration and database
│   │   ├── models/           # Database models
│   │   ├── schemas/          # Pydantic schemas
│   │   └── services/         # Business logic services
│   ├── templates/            # HTML report templates
│   │   └── reports/          # Market Intelligence & Cover Letter templates
│   ├── generated_reports/    # Generated reports (gitignored)
│   ├── requirements.txt      # Python dependencies
│   └── crane_intelligence.db # SQLite database
├── frontend/                 # Frontend web interface
│   ├── css/                  # Stylesheets
│   ├── images/               # Images and assets
│   ├── homepage.html         # Marketing homepage
│   ├── dashboard.html        # User dashboard
│   ├── report-generation.html # Report generation interface
│   ├── login.html            # User authentication
│   └── valuation_terminal.html # Bloomberg-style terminal
├── docs/                     # Documentation and requirements
│   └── requirements/         # Project requirements and sample data
├── data/                     # Data files (gitignored)
├── run_backend.py           # Backend startup script
├── start_platform.bat       # Windows startup script
└── .gitignore              # Git ignore rules
```

## 🚀 **Quick Start**

### **Option 1: Windows Batch Script (Recommended)**
```bash
# Double-click this file:
start_platform.bat
```

### **Option 2: Manual Startup**
```bash
# Terminal 1: Start Backend
python run_backend.py

# Terminal 2: Start Frontend  
python -m http.server 3000 --directory frontend
```

## 🌐 **Access Points**

- **Marketing Homepage**: http://localhost:3000/homepage.html
- **Platform Application**: http://localhost:3000
- **Backend API**: http://localhost:8003
- **API Documentation**: http://localhost:8003/docs
- **Health Check**: http://localhost:8003/health

## 🔐 **Demo Credentials**

- **Email**: demo@craneintelligence.com
- **Password**: DemoOnly123
- **Subscription**: Pro Tier (access to all features)

## 💰 **Subscription Plans**

| Plan | Price | Features |
|------|-------|----------|
| **Basic** | $999/month | 50 valuations/month, Core valuation, Market comparables |
| **Pro** | $2499/month | 200 valuations/month, Deal Score, Portfolio analysis, API access |
| **Enterprise** | Custom | Unlimited access, Custom integrations, Dedicated support |

## 🎯 **Target Customers**

- **Crane Rental Companies** - Fleet valuation & optimization
- **Equipment Dealers** - Inventory pricing & services
- **Financial Institutions** - Collateral assessment

## 🛠️ **Technology Stack**

- **Backend**: FastAPI, Python 3.12
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Authentication**: JWT, bcrypt
- **Database**: SQLAlchemy models (ready for PostgreSQL)
- **Deployment**: Python HTTP server (production-ready for Nginx/Apache)

## 📊 **Key Features**

### **Dual Report Generation**
- **Market Intelligence Report**: Comprehensive market analysis with equipment specifications, market analysis, valuation summary, and recommendations
- **Cover Letter**: Professional business letter format with equipment summary and valuation highlights
- Both reports generated simultaneously for each valuation request

### **API Endpoints**

#### **Authentication**
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/profile` - User profile
- `GET /api/v1/auth/subscription/plans` - Available plans

#### **Valuation**
- `POST /api/v1/valuation/value-crane` - Crane valuation
- `POST /api/v1/valuation/market-analysis` - Market analysis
- `POST /api/v1/valuation/fleet-optimization` - Portfolio analysis (Pro+)
- `GET /api/v1/valuation/subscription/limits` - Usage limits

#### **Reports**
- `POST /api/v1/reports/generate` - Generate dual reports
- `GET /api/v1/reports/download/{report_id}/market_intelligence` - Download Market Intelligence Report
- `GET /api/v1/reports/download/{report_id}/cover_letter` - Download Cover Letter

## 🔧 **Development**

### **Install Dependencies**
```bash
cd backend
pip install -r requirements.txt
```

### **Run Development Server**
```bash
cd backend
python main.py
```

### **Test API**
```bash
# Health check
curl http://localhost:8000/health

# Authentication health
curl http://localhost:8000/api/v1/auth/health
```

## 🎉 **Status: PRODUCTION READY**

The platform is fully functional with:
- Professional-grade valuation engine
- Secure authentication system
- Subscription-based access control
- Modern web interface
- Comprehensive API documentation
- Clean, organized project structure

---

**Built with ❤️ for the Crane Industry**