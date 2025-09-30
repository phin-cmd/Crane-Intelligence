@echo off
echo FRESH DEPLOYMENT - CRANE INTELLIGENCE PLATFORM
echo ==============================================

set SERVER=root@159.65.186.73
set PROJECT_DIR=/var/www/crane-intelligence

echo 1. Stopping all services on server...
ssh %SERVER% "cd %PROJECT_DIR% && docker-compose down"
ssh %SERVER% "systemctl stop nginx"

echo 2. Clearing old code and caches...
ssh %SERVER% "rm -rf %PROJECT_DIR%/*"
ssh %SERVER% "rm -rf /var/cache/nginx/*"
ssh %SERVER% "docker system prune -f"

echo 3. Creating fresh project directory...
ssh %SERVER% "mkdir -p %PROJECT_DIR%"

echo 4. Uploading fresh code...

echo Uploading backend files...
scp -r backend %SERVER%:%PROJECT_DIR%/
scp -r frontend %SERVER%:%PROJECT_DIR%/
scp docker-compose.yml %SERVER%:%PROJECT_DIR%/
scp Dockerfile %SERVER%:%PROJECT_DIR%/
scp requirements.txt %SERVER%:%PROJECT_DIR%/

echo 5. Setting up fresh environment on server...
ssh %SERVER% "cd %PROJECT_DIR% && chmod +x *.sh"

echo 6. Starting services with fresh code...
ssh %SERVER% "cd %PROJECT_DIR% && docker-compose up -d"

echo 7. Waiting for services to start...
timeout /t 10 /nobreak

echo 8. Testing deployment...
ssh %SERVER% "curl -s http://127.0.0.1:3001 | head -5"
ssh %SERVER% "curl -s http://127.0.0.1:8004/health"

echo 9. Restarting Nginx...
ssh %SERVER% "systemctl start nginx"
ssh %SERVER% "systemctl reload nginx"

echo 10. Final verification...
ssh %SERVER% "curl -s https://craneintelligence.tech | grep -i 'Crane Intelligence'"

echo.
echo FRESH DEPLOYMENT COMPLETE!
echo Domain: https://craneintelligence.tech
echo API Health: https://craneintelligence.tech/api/v1/database/health
echo API Docs: https://craneintelligence.tech/docs
echo.
echo Test Login Credentials:
echo Admin: admin@craneintelligence.com / admin123
echo User: user@craneintelligence.com / user123
