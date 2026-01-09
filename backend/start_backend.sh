#!/bin/bash
# Backend startup script with DigitalOcean Spaces configuration
# NOTE: Set DO_SPACES_KEY, DO_SPACES_SECRET, and other env vars before running this script
# Or load them from a .env file (which should NOT be committed to git)

# Load environment variables from .env if it exists
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
    echo "✅ Loaded environment variables from .env"
else
    echo "⚠️  .env file not found. Make sure DO_SPACES_KEY, DO_SPACES_SECRET, etc. are set."
fi

# Set defaults for non-sensitive config
export DO_SPACES_REGION=${DO_SPACES_REGION:-'atl1'}
export DO_SPACES_BUCKET=${DO_SPACES_BUCKET:-'crane-intelligence-storage'}
export ENVIRONMENT=${ENVIRONMENT:-'prod'}

cd /root/crane/backend

# Start uvicorn with environment variables
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8004 --reload
