#!/usr/bin/env python3
"""
Database Initialization Script for Crane Intelligence Platform
This script creates the necessary database tables
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://crane_user:crane_password@localhost:5434/crane_db")

def create_tables():
    """Create database tables"""
    try:
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            print("✅ Database connection successful")
            print(f"PostgreSQL version: {result.fetchone()[0]}")
        
        # Create tables using SQL
        create_tables_sql = """
        -- Create users table
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            hashed_password VARCHAR(255) NOT NULL,
            full_name VARCHAR(255) NOT NULL,
            username VARCHAR(255) UNIQUE,
            company_name VARCHAR(255),
            user_role VARCHAR(50) DEFAULT 'user',
            subscription_tier VARCHAR(50) DEFAULT 'basic',
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        );
        
        -- Create crane_listings table
        CREATE TABLE IF NOT EXISTS crane_listings (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            description TEXT,
            price VARCHAR(100),
            location VARCHAR(255),
            crane_type VARCHAR(100),
            year VARCHAR(10),
            condition VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Create consultations table
        CREATE TABLE IF NOT EXISTS consultations (
            id SERIAL PRIMARY KEY,
            user_id INTEGER,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            phone VARCHAR(50),
            message TEXT,
            status VARCHAR(50) DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Create indexes
        CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
        CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
        CREATE INDEX IF NOT EXISTS idx_crane_listings_type ON crane_listings(crane_type);
        CREATE INDEX IF NOT EXISTS idx_consultations_email ON consultations(email);
        """
        
        # Execute SQL
        with engine.connect() as conn:
            conn.execute(text(create_tables_sql))
            conn.commit()
            print("✅ Database tables created successfully")
        
        # Verify tables exist
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name;
            """))
            tables = [row[0] for row in result.fetchall()]
            print(f"✅ Tables created: {', '.join(tables)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating tables: {str(e)}")
        return False

def insert_sample_data():
    """Insert sample data for testing"""
    try:
        engine = create_engine(DATABASE_URL)
        
        # Sample crane listings
        sample_listings = [
            {
                'title': 'Liebherr LTM 1200-5.1 Mobile Crane',
                'description': 'Excellent condition mobile crane, perfect for construction projects',
                'price': '$450,000',
                'location': 'Houston, TX',
                'crane_type': 'Mobile Crane',
                'year': '2018',
                'condition': 'Excellent'
            },
            {
                'title': 'Terex AC 1000 Tower Crane',
                'description': 'High-capacity tower crane for large construction projects',
                'price': '$320,000',
                'location': 'Los Angeles, CA',
                'crane_type': 'Tower Crane',
                'year': '2019',
                'condition': 'Very Good'
            },
            {
                'title': 'Caterpillar 320D Crawler Crane',
                'description': 'Heavy-duty crawler crane with excellent lifting capacity',
                'price': '$280,000',
                'location': 'Chicago, IL',
                'crane_type': 'Crawler Crane',
                'year': '2017',
                'condition': 'Good'
            }
        ]
        
        with engine.connect() as conn:
            for listing in sample_listings:
                conn.execute(text("""
                    INSERT INTO crane_listings (title, description, price, location, crane_type, year, condition)
                    VALUES (:title, :description, :price, :location, :crane_type, :year, :condition)
                """), listing)
            conn.commit()
            print("✅ Sample crane listings inserted")
        
        return True
        
    except Exception as e:
        print(f"❌ Error inserting sample data: {str(e)}")
        return False

def main():
    """Main function"""
    print("=== Crane Intelligence Database Initialization ===")
    
    # Create tables
    if create_tables():
        print("✅ Database initialization completed successfully")
        
        # Insert sample data
        if insert_sample_data():
            print("✅ Sample data inserted successfully")
        else:
            print("⚠️  Sample data insertion failed, but tables are created")
    else:
        print("❌ Database initialization failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
