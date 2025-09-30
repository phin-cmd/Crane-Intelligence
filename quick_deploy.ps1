# Quick Deploy Script
Write-Host "Quick Deploy - Crane Intelligence Platform" -ForegroundColor Green

# Upload key files
Write-Host "Uploading key files..." -ForegroundColor Yellow
scp backend/app/auth_endpoints.py root@159.65.186.73:/var/www/crane-intelligence/backend/app/
scp backend/app/auth_schemas.py root@159.65.186.73:/var/www/crane-intelligence/backend/app/
scp backend/app/auth_utils.py root@159.65.186.73:/var/www/crane-intelligence/backend/app/
scp backend/app/models.py root@159.65.186.73:/var/www/crane-intelligence/backend/app/
scp backend/app/config.py root@159.65.186.73:/var/www/crane-intelligence/backend/app/
scp backend/app/main_simple.py root@159.65.186.73:/var/www/crane-intelligence/backend/app/main.py
scp frontend/js/auth.js root@159.65.186.73:/var/www/crane-intelligence/frontend/js/
scp backend/requirements.txt root@159.65.186.73:/var/www/crane-intelligence/backend/

Write-Host "Restarting services..." -ForegroundColor Yellow
ssh root@159.65.186.73 "cd /var/www/crane-intelligence && docker-compose restart"

Write-Host "Testing deployment..." -ForegroundColor Yellow
ssh root@159.65.186.73 "curl -s https://craneintelligence.tech | grep -i 'Crane Intelligence'"

Write-Host "Deployment complete!" -ForegroundColor Green
