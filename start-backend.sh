#!/bin/bash
# Start backend and verify it's running

cd /root/crane

echo "=========================================="
echo "STARTING BACKEND CONTAINER"
echo "=========================================="
echo ""

echo "Step 1: Checking current container status..."
docker-compose ps

echo ""
echo "Step 2: Starting all services..."
docker-compose up -d

echo ""
echo "Step 3: Waiting for services to start (20 seconds)..."
sleep 20

echo ""
echo "Step 4: Checking container status again..."
docker-compose ps

echo ""
echo "Step 5: Checking backend logs..."
docker-compose logs --tail=50 backend | tail -30

echo ""
echo "Step 6: Testing backend connection..."
for i in {1..5}; do
    echo "Attempt $i..."
    if curl -s -o /dev/null -w "HTTP %{http_code}\n" http://localhost:8004/api/v1/health; then
        echo "✓ Backend is responding!"
        break
    else
        echo "✗ Backend not responding yet, waiting 5 seconds..."
        sleep 5
    fi
done

echo ""
echo "Step 7: Final status check..."
docker-compose ps

echo ""
echo "=========================================="
echo "STARTUP COMPLETE"
echo "=========================================="
echo ""
echo "If backend is still not responding:"
echo "1. Check logs: docker-compose logs backend"
echo "2. Check if port 8004 is in use: netstat -tuln | grep 8004"
echo "3. Try rebuilding: docker-compose build --no-cache backend"
echo ""

