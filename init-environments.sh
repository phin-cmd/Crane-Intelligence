#!/bin/bash
set -e

echo "========================================="
echo "Initializing Dev and UAT Environments"
echo "========================================="

cd /root/crane

# Create env files from templates if they don't exist
if [ ! -f config/dev.env ]; then
    echo "Creating config/dev.env from template..."
    cp config/dev.env.template config/dev.env
    chmod 600 config/dev.env
    echo "⚠️  Please edit config/dev.env and fill in real values for API keys, etc."
fi

if [ ! -f config/uat.env ]; then
    echo "Creating config/uat.env from template..."
    cp config/uat.env.template config/uat.env
    chmod 600 config/uat.env
    echo "⚠️  Please edit config/uat.env and fill in real values for API keys, etc."
fi

if [ ! -f config/prod.env ]; then
    echo "Creating config/prod.env from template..."
    cp config/prod.env.template config/prod.env
    chmod 600 config/prod.env
    echo "⚠️  Please edit config/prod.env and fill in real values for API keys, etc."
fi

echo ""
echo "Step 1: Starting dev database..."
docker compose -f docker-compose.dev.yml -p crane-dev up -d db

echo "Waiting for dev database to be ready..."
sleep 5

echo ""
echo "Step 2: Starting UAT database..."
docker compose -f docker-compose.uat.yml -p crane-uat up -d db

echo "Waiting for UAT database to be ready..."
sleep 5

echo ""
echo "Step 3: Running database migrations for dev..."
# Run migrations if you have a migration command
# docker compose -f docker-compose.dev.yml -p crane-dev exec backend alembic upgrade head
# OR: docker compose -f docker-compose.dev.yml -p crane-dev exec backend python -m app.migrate
echo "⚠️  Run your migration command manually for dev environment"

echo ""
echo "Step 4: Running database migrations for UAT..."
# docker compose -f docker-compose.uat.yml -p crane-uat exec backend alembic upgrade head
echo "⚠️  Run your migration command manually for UAT environment"

echo ""
echo "========================================="
echo "Environment initialization complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Edit config/dev.env, config/uat.env, and config/prod.env with real API keys"
echo "2. Run database migrations for dev and UAT"
echo "3. Start full stacks:"
echo "   - Dev:  docker compose -f docker-compose.dev.yml -p crane-dev up -d"
echo "   - UAT:  docker compose -f docker-compose.uat.yml -p crane-uat up -d"
echo ""

