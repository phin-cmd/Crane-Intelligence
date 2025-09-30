# Crane Intelligence Platform

Professional Crane Valuation & Market Intelligence Platform built with FastAPI and modern web technologies.

## Features

- **Real-Time Market Data**: Live market data, pricing trends, and equipment valuations
- **Advanced Analytics**: Comprehensive valuation models and predictive analytics
- **Professional Tools**: Industry-standard tools for equipment inspection and compliance
- **Bloomberg Terminal Design**: Professional black and green interface
- **JWT Authentication**: Secure user authentication system
- **Docker Support**: Containerized deployment with Docker Compose

## Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **PostgreSQL**: Production database
- **Redis**: Caching and session storage
- **JWT**: Authentication tokens
- **Docker**: Containerization

### Frontend
- **HTML5/CSS3**: Modern web standards
- **JavaScript**: Interactive functionality
- **Nginx**: Web server and reverse proxy
- **Responsive Design**: Mobile-friendly interface

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd crane-intelligence
   ```

2. **Start the services**
   ```bash
   docker-compose up -d
   ```

3. **Access the application**
   - Frontend: http://localhost:3001
   - Backend API: http://localhost:8004
   - Database Admin: http://localhost:8082

### Demo Credentials
- **Email**: test@craneintelligence.com
- **Password**: password123

## Project Structure

```
crane-intelligence/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── main.py        # Main application
│   │   ├── config.py      # Configuration
│   │   └── requirements.txt
│   └── Dockerfile
├── frontend/              # Frontend application
│   ├── homepage.html      # Main landing page
│   ├── js/                # JavaScript files
│   ├── css/               # Stylesheets
│   ├── images/            # Assets
│   ├── nginx.conf         # Nginx configuration
│   └── Dockerfile
├── docker-compose.yml     # Docker services
└── README.md
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration

### Health Check
- `GET /api/v1/health` - API health status

## Development

### Backend Development
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Development
```bash
cd frontend
python -m http.server 8000
```

## Production Deployment

### Digital Ocean Deployment
1. **Connect to server**
   ```bash
   ssh root@your-server-ip
   ```

2. **Clone repository**
   ```bash
   git clone <repository-url>
   cd crane-intelligence
   ```

3. **Start services**
   ```bash
   docker-compose up -d
   ```

4. **Configure Nginx** (if needed)
   ```bash
   # Configure domain and SSL
   ```

## Environment Variables

Create a `.env` file in the root directory:

```env
DATABASE_URL=postgresql://crane_user:crane_password@db:5432/crane_db
SECRET_KEY=your-secret-key
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

© 2024 Crane Intelligence. All rights reserved.

## Support

For support and questions, please contact the development team.