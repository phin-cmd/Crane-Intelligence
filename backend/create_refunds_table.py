#!/usr/bin/env python3
"""
Migration script to create refunds table
"""
import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://crane_user:crane_password@localhost:5434/crane_intelligence")

def create_refunds_table():
    """Create the refunds table"""
    try:
        import urllib.parse
        parsed = urllib.parse.urlparse(DATABASE_URL)
        
        conn = psycopg2.connect(
            host=parsed.hostname or "localhost",
            port=parsed.port or 5434,
            database=parsed.path[1:] if parsed.path else "crane_intelligence",
            user=parsed.username or "crane_user",
            password=parsed.password or "crane_password"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'refunds'
            );
        """)
        exists = cursor.fetchone()[0]
        
        if exists:
            print("✓ Refunds table already exists")
            return
        
        # Create the table
        create_sql = """
        CREATE TABLE refunds (
            id SERIAL PRIMARY KEY,
            payment_id INTEGER NOT NULL REFERENCES payments(id),
            user_id INTEGER NOT NULL REFERENCES users(id),
            stripe_refund_id VARCHAR UNIQUE,
            amount FLOAT NOT NULL,
            currency VARCHAR DEFAULT 'USD',
            status VARCHAR DEFAULT 'pending',
            reason TEXT,
            processed_by INTEGER REFERENCES admin_users(id),
            admin_notes TEXT,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW(),
            processed_at TIMESTAMP
        );
        
        CREATE INDEX IF NOT EXISTS idx_refunds_payment_id ON refunds(payment_id);
        CREATE INDEX IF NOT EXISTS idx_refunds_user_id ON refunds(user_id);
        CREATE INDEX IF NOT EXISTS idx_refunds_stripe_refund_id ON refunds(stripe_refund_id);
        CREATE INDEX IF NOT EXISTS idx_refunds_status ON refunds(status);
        CREATE INDEX IF NOT EXISTS idx_refunds_created_at ON refunds(created_at);
        """
        
        cursor.execute(create_sql)
        print("✓ Refunds table created successfully")
        print("✓ Indexes created successfully")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error creating refunds table: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    create_refunds_table()

