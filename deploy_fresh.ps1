# Fresh Deployment Script for Crane Intelligence Platform
Write-Host "FRESH DEPLOYMENT - CRANE INTELLIGENCE PLATFORM" -ForegroundColor Green
Write-Host "==============================================" -ForegroundColor Green

$SERVER = "root@159.65.186.73"
$PROJECT_DIR = "/var/www/crane-intelligence"

Write-Host "1. Stopping all services on server..." -ForegroundColor Yellow
ssh $SERVER "cd $PROJECT_DIR && docker-compose down"
ssh $SERVER "systemctl stop nginx"

Write-Host "2. Clearing old code and caches..." -ForegroundColor Yellow
ssh $SERVER "rm -rf $PROJECT_DIR/*"
ssh $SERVER "rm -rf /var/cache/nginx/*"
ssh $SERVER "docker system prune -f"

Write-Host "3. Creating fresh project directory..." -ForegroundColor Yellow
ssh $SERVER "mkdir -p $PROJECT_DIR"

Write-Host "4. Uploading fresh code..." -ForegroundColor Yellow

# Upload backend files
Write-Host "Uploading backend files..." -ForegroundColor Cyan
scp -r .\backend $SERVER`:$PROJECT_DIR/
scp -r .\frontend $SERVER`:$PROJECT_DIR/
scp .\docker-compose.yml $SERVER`:$PROJECT_DIR/
scp .\Dockerfile $SERVER`:$PROJECT_DIR/
scp .\requirements.txt $SERVER`:$PROJECT_DIR/

Write-Host "5. Setting up fresh environment on server..." -ForegroundColor Yellow
ssh $SERVER "cd $PROJECT_DIR && chmod +x *.sh"

Write-Host "6. Starting services with fresh code..." -ForegroundColor Yellow
ssh $SERVER "cd $PROJECT_DIR && docker-compose up -d"

Write-Host "7. Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep 10

Write-Host "8. Testing deployment..." -ForegroundColor Yellow
ssh $SERVER "curl -s http://127.0.0.1:3001 | head -5"
ssh $SERVER "curl -s http://127.0.0.1:8004/health"

Write-Host "9. Restarting Nginx..." -ForegroundColor Yellow
ssh $SERVER "systemctl start nginx"
ssh $SERVER "systemctl reload nginx"

Write-Host "10. Final verification..." -ForegroundColor Yellow
ssh $SERVER "curl -s https://craneintelligence.tech | grep -i 'Crane Intelligence'"

Write-Host ""
Write-Host "FRESH DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "Domain: https://craneintelligence.tech" -ForegroundColor Cyan
Write-Host "API Health: https://craneintelligence.tech/api/v1/database/health" -ForegroundColor Cyan
Write-Host "API Docs: https://craneintelligence.tech/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Test Login Credentials:" -ForegroundColor Yellow
Write-Host "Admin: admin@craneintelligence.com / admin123" -ForegroundColor White
Write-Host "User: user@craneintelligence.com / user123" -ForegroundColor White
