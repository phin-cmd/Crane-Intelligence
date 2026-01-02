#!/bin/bash

echo "=========================================="
echo "Visitor Tracking Table Verification & Creation"
echo "=========================================="
echo ""

# Method 1: Check via Python
echo "Method 1: Checking via Python..."
docker exec crane-backend-1 python3 -c "
from app.core.database import engine
from sqlalchemy import inspect
try:
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    if 'visitor_tracking' in tables:
        print('✅ visitor_tracking table EXISTS')
        columns = inspector.get_columns('visitor_tracking')
        print(f'   Table has {len(columns)} columns')
    else:
        print('❌ visitor_tracking table DOES NOT EXIST')
        print('   Available tables:', ', '.join(sorted(tables)))
except Exception as e:
    print(f'❌ Error: {e}')
" 2>&1

echo ""
echo "Method 2: Creating table if it doesn't exist..."
docker exec crane-backend-1 python3 /app/create_visitor_tracking_table.py 2>&1

echo ""
echo "Method 3: Verifying via SQL..."
docker exec crane-db-1 psql -U crane_user -d crane_intelligence -c "\d visitor_tracking" 2>&1 | head -20

echo ""
echo "=========================================="
echo "Verification Complete"
echo "=========================================="

