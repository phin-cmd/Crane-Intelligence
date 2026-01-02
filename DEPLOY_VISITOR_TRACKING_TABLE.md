# Deploy Visitor Tracking Table to All Environments

## Table Name
**`visitor_tracking`**

This table stores all website visitor analytics data including:
- Visitor identification (visitor_id, session_id, user_id)
- Page information (page_url, page_title, referrer)
- Device & browser information
- Location data (country, region, city)
- Engagement metrics (time_on_page, scroll_depth, bounce_rate)
- Traffic source data

## Quick Creation Methods

### Method 1: Using Python Script (Recommended)

```bash
# In dev/UAT/production backend container or server
cd /root/crane/backend
python3 create_visitor_tracking_table.py
```

### Method 2: Using SQL Script (PostgreSQL)

```bash
# Connect to your database
psql -h <host> -U crane_user -d crane_intelligence

# Run the SQL script
\i /root/crane/backend/migrations/create_visitor_tracking_table.sql

# Or directly:
psql -h <host> -U crane_user -d crane_intelligence -f /root/crane/backend/migrations/create_visitor_tracking_table.sql
```

### Method 3: Using Docker (if backend is containerized)

```bash
# For dev
docker exec crane-backend-1 python3 /app/create_visitor_tracking_table.py

# Or using SQL
docker exec -i crane-db-1 psql -U crane_user -d crane_intelligence < /root/crane/backend/migrations/create_visitor_tracking_table.sql
```

### Method 4: Restart Backend (Auto-creation)

The table should be created automatically when the backend starts if:
1. The model is imported in `app/core/database.py` ✅ (already done)
2. `init_db()` is called on startup ✅ (already done)

Simply restart the backend:
```bash
docker restart crane-backend-1
# or
systemctl restart crane-backend
```

## Verify Table Exists

### Using Python
```python
from app.core.database import engine
from sqlalchemy import inspect
inspector = inspect(engine)
tables = inspector.get_table_names()
print('visitor_tracking' in tables)  # Should print True
```

### Using SQL
```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name = 'visitor_tracking';
```

### Using psql
```bash
psql -h <host> -U crane_user -d crane_intelligence -c "\d visitor_tracking"
```

## Table Structure

The table has the following key columns:
- `id` (Primary Key)
- `visitor_id` (Indexed)
- `session_id` (Indexed)
- `user_id` (Indexed, nullable)
- `page_url`
- `page_title`
- `referrer`
- `browser`, `device_type`, `os`
- `country`, `region`, `city`
- `time_on_page`, `scroll_depth`
- `traffic_source`
- `visited_at` (Indexed, timestamp)
- And many more...

## Environment-Specific Instructions

### Development
```bash
cd /root/crane/backend
python3 create_visitor_tracking_table.py
```

### UAT
```bash
# SSH into UAT server
cd /root/crane/backend
python3 create_visitor_tracking_table.py
```

### Production
```bash
# SSH into production server
cd /root/crane/backend
python3 create_visitor_tracking_table.py

# Or use database migration tool if available
```

## Troubleshooting

### Table Not Created After Restart
1. Check backend logs for errors:
   ```bash
   docker logs crane-backend-1 | grep -i visitor
   ```

2. Check if model is imported:
   ```bash
   grep -r "visitor_tracking" /root/crane/backend/app/core/database.py
   ```

3. Manually create using SQL script

### Permission Errors
Ensure the database user has CREATE TABLE permissions:
```sql
GRANT CREATE ON DATABASE crane_intelligence TO crane_user;
```

### Connection Errors
Verify database connection string in environment variables:
```bash
echo $DATABASE_URL
```

## Next Steps

After creating the table:
1. Verify it exists using one of the methods above
2. Test tracking by visiting a page
3. Check admin analytics dashboard to see data
4. Monitor table growth:
   ```sql
   SELECT COUNT(*) FROM visitor_tracking;
   ```

