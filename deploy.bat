@echo off
REM Crane Intelligence Platform - Windows Production Deployment Script

echo 🚀 Starting Crane Intelligence Platform Deployment...

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not installed. Please install Docker Desktop first.
    pause
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose is not installed. Please install Docker Compose first.
    pause
    exit /b 1
)

REM Create necessary directories
echo 📁 Creating necessary directories...
if not exist "logs" mkdir logs
if not exist "data" mkdir data
if not exist "backups" mkdir backups
if not exist "ssl" mkdir ssl

REM Copy environment file
if not exist ".env" (
    echo 📋 Creating environment file...
    copy env.production .env
    echo ⚠️  Please update .env file with your production values
)

REM Build and start services
echo 🔨 Building and starting services...
docker-compose down --remove-orphans
docker-compose build --no-cache
docker-compose up -d

REM Wait for services to be ready
echo ⏳ Waiting for services to be ready...
timeout /t 30 /nobreak >nul

REM Check service health
echo 🏥 Checking service health...
curl -f http://localhost:8003/health >nul 2>&1
if errorlevel 1 (
    echo ❌ Backend service is not responding
    pause
    exit /b 1
) else (
    echo ✅ Backend service is healthy
)

curl -f http://localhost:3000 >nul 2>&1
if errorlevel 1 (
    echo ❌ Frontend service is not responding
    pause
    exit /b 1
) else (
    echo ✅ Frontend service is healthy
)

REM Initialize database
echo 🗄️ Initializing database...
docker-compose exec backend python init_equipment_db.py

echo 🎉 Deployment completed successfully!
echo.
echo 🌐 Access Points:
echo    Frontend: http://localhost:3000
echo    Backend API: http://localhost:8003
echo    API Docs: http://localhost:8003/docs
echo.
echo 📊 Service Status:
docker-compose ps

pause

