@echo off
echo Starting Crane Intelligence Platform...
echo.

echo Starting Backend Server...
start "Backend Server" cmd /k "python run_backend.py"

echo Waiting for backend to start...
timeout /t 5 /nobreak > nul

echo Starting Frontend Server...
start "Frontend Server" cmd /k "python -m http.server 3000 --directory frontend"

echo.
echo Platform started successfully!
echo.
echo Access Points:
echo - Homepage: http://localhost:3000/homepage.html
echo - Dashboard: http://localhost:3000/dashboard.html
echo - Report Generation: http://localhost:3000/report-generation.html
echo - Backend API: http://localhost:8003
echo - API Documentation: http://localhost:8003/docs
echo.
echo Demo Credentials:
echo - Email: demo@craneintelligence.com
echo - Password: DemoOnly123
echo.
pause