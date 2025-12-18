"""
PostgreSQL Database Security
Implements comprehensive database security measures
"""

import os
import logging
import asyncio
import hashlib
import secrets
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import asyncpg
from sqlalchemy import text, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
import redis
import bcrypt

logger = logging.getLogger(__name__)

class DatabaseSecurityManager:
    """PostgreSQL Database Security Management"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.redis_client = None
        self.connection_pool = None
        self.security_config = {
            "max_connections": 20,
            "connection_timeout": 30,
            "query_timeout": 60,
            "max_retries": 3,
            "enable_ssl": True,
            "ssl_mode": "require",
            "enable_encryption": True,
            "audit_logging": True,
            "failed_login_threshold": 5,
            "lockout_duration": 300,  # 5 minutes
        }
    
    async def initialize(self):
        """Initialize database security components"""
        try:
            # Initialize Redis for security caching
            try:
                self.redis_client = redis.Redis(
                    host='localhost', 
                    port=6379, 
                    db=3, 
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5
                )
                await self.redis_client.ping()
                logger.info("Redis connection established for database security")
            except Exception as e:
                logger.warning(f"Redis not available for database security: {e}")
                self.redis_client = None
            
            # Create connection pool with security settings
            self.connection_pool = await asyncpg.create_pool(
                self.database_url,
                min_size=5,
                max_size=self.security_config["max_connections"],
                command_timeout=self.security_config["query_timeout"],
                server_settings={
                    'application_name': 'crane_intelligence_secure',
                    'statement_timeout': str(self.security_config["query_timeout"] * 1000),
                    'idle_in_transaction_session_timeout': '300000',
                    'lock_timeout': '10000',
                }
            )
            
            # Create security tables
            await self.create_security_tables()
            
            logger.info("Database security manager initialized")
            
        except Exception as e:
            logger.error(f"Error initializing database security: {e}")
            raise
    
    async def create_security_tables(self):
        """Create security-related database tables"""
        try:
            async with self.connection_pool.acquire() as conn:
                # Create audit log table
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS security_audit_log (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER,
                        action VARCHAR(100) NOT NULL,
                        table_name VARCHAR(100),
                        record_id INTEGER,
                        old_values JSONB,
                        new_values JSONB,
                        ip_address INET,
                        user_agent TEXT,
                        timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        success BOOLEAN DEFAULT TRUE,
                        error_message TEXT
                    );
                """)
                
                # Create failed login attempts table
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS failed_login_attempts (
                        id SERIAL PRIMARY KEY,
                        email VARCHAR(255) NOT NULL,
                        ip_address INET NOT NULL,
                        user_agent TEXT,
                        attempt_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        success BOOLEAN DEFAULT FALSE,
                        failure_reason VARCHAR(100)
                    );
                """)
                
                # Create database access logs table
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS database_access_log (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER,
                        query_type VARCHAR(50),
                        table_name VARCHAR(100),
                        query_hash VARCHAR(64),
                        execution_time_ms INTEGER,
                        rows_affected INTEGER,
                        ip_address INET,
                        timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    );
                """)
                
                # Create indexes for performance
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp 
                    ON security_audit_log(timestamp);
                """)
                
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_audit_log_user_id 
                    ON security_audit_log(user_id);
                """)
                
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_failed_logins_email 
                    ON failed_login_attempts(email, attempt_time);
                """)
                
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_failed_logins_ip 
                    ON failed_login_attempts(ip_address, attempt_time);
                """)
                
                logger.info("Security tables created successfully")
                
        except Exception as e:
            logger.error(f"Error creating security tables: {e}")
            raise
    
    async def log_audit_event(self, 
                            user_id: Optional[int],
                            action: str,
                            table_name: Optional[str] = None,
                            record_id: Optional[int] = None,
                            old_values: Optional[Dict] = None,
                            new_values: Optional[Dict] = None,
                            ip_address: Optional[str] = None,
                            user_agent: Optional[str] = None,
                            success: bool = True,
                            error_message: Optional[str] = None):
        """Log security audit events"""
        try:
            async with self.connection_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO security_audit_log 
                    (user_id, action, table_name, record_id, old_values, new_values, 
                     ip_address, user_agent, success, error_message)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                """, user_id, action, table_name, record_id, old_values, new_values,
                   ip_address, user_agent, success, error_message)
                
        except Exception as e:
            logger.error(f"Error logging audit event: {e}")
    
    async def log_failed_login(self, 
                             email: str,
                             ip_address: str,
                             user_agent: Optional[str] = None,
                             failure_reason: str = "Invalid credentials"):
        """Log failed login attempts"""
        try:
            async with self.connection_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO failed_login_attempts 
                    (email, ip_address, user_agent, failure_reason)
                    VALUES ($1, $2, $3, $4)
                """, email, ip_address, user_agent, failure_reason)
                
        except Exception as e:
            logger.error(f"Error logging failed login: {e}")
    
    async def check_account_lockout(self, email: str, ip_address: str) -> bool:
        """Check if account is locked out due to failed attempts"""
        try:
            threshold_time = datetime.now() - timedelta(seconds=self.security_config["lockout_duration"])
            
            async with self.connection_pool.acquire() as conn:
                # Check by email
                email_attempts = await conn.fetchval("""
                    SELECT COUNT(*) FROM failed_login_attempts 
                    WHERE email = $1 AND attempt_time > $2 AND success = FALSE
                """, email, threshold_time)
                
                # Check by IP
                ip_attempts = await conn.fetchval("""
                    SELECT COUNT(*) FROM failed_login_attempts 
                    WHERE ip_address = $1 AND attempt_time > $2 AND success = FALSE
                """, ip_address, threshold_time)
                
                return (email_attempts >= self.security_config["failed_login_threshold"] or 
                       ip_attempts >= self.security_config["failed_login_threshold"])
                
        except Exception as e:
            logger.error(f"Error checking account lockout: {e}")
            return False
    
    async def log_database_access(self, 
                                user_id: Optional[int],
                                query_type: str,
                                table_name: str,
                                query_hash: str,
                                execution_time_ms: int,
                                rows_affected: int,
                                ip_address: Optional[str] = None):
        """Log database access for monitoring"""
        try:
            async with self.connection_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO database_access_log 
                    (user_id, query_type, table_name, query_hash, execution_time_ms, 
                     rows_affected, ip_address)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                """, user_id, query_type, table_name, query_hash, execution_time_ms,
                   rows_affected, ip_address)
                
        except Exception as e:
            logger.error(f"Error logging database access: {e}")
    
    def hash_query(self, query: str) -> str:
        """Create a hash of the query for logging"""
        return hashlib.sha256(query.encode()).hexdigest()
    
    async def execute_secure_query(self, 
                                 query: str,
                                 params: tuple = (),
                                 user_id: Optional[int] = None,
                                 ip_address: Optional[str] = None) -> Any:
        """Execute query with security logging"""
        start_time = datetime.now()
        query_hash = self.hash_query(query)
        
        try:
            async with self.connection_pool.acquire() as conn:
                # Execute query
                result = await conn.fetch(query, *params)
                
                # Calculate execution time
                execution_time = (datetime.now() - start_time).total_seconds() * 1000
                
                # Log database access
                await self.log_database_access(
                    user_id=user_id,
                    query_type="SELECT",
                    table_name="unknown",  # Could be parsed from query
                    query_hash=query_hash,
                    execution_time_ms=int(execution_time),
                    rows_affected=len(result),
                    ip_address=ip_address
                )
                
                return result
                
        except Exception as e:
            # Log failed query
            await self.log_audit_event(
                user_id=user_id,
                action="database_query_failed",
                ip_address=ip_address,
                success=False,
                error_message=str(e)
            )
            raise
    
    async def get_security_stats(self) -> Dict[str, Any]:
        """Get database security statistics"""
        try:
            async with self.connection_pool.acquire() as conn:
                # Get failed login attempts in last 24 hours
                failed_logins_24h = await conn.fetchval("""
                    SELECT COUNT(*) FROM failed_login_attempts 
                    WHERE attempt_time > NOW() - INTERVAL '24 hours'
                """)
                
                # Get unique IPs with failed attempts
                suspicious_ips = await conn.fetchval("""
                    SELECT COUNT(DISTINCT ip_address) FROM failed_login_attempts 
                    WHERE attempt_time > NOW() - INTERVAL '24 hours'
                """)
                
                # Get audit log entries in last 24 hours
                audit_entries_24h = await conn.fetchval("""
                    SELECT COUNT(*) FROM security_audit_log 
                    WHERE timestamp > NOW() - INTERVAL '24 hours'
                """)
                
                # Get database access stats
                db_access_24h = await conn.fetchval("""
                    SELECT COUNT(*) FROM database_access_log 
                    WHERE timestamp > NOW() - INTERVAL '24 hours'
                """)
                
                return {
                    "failed_logins_24h": failed_logins_24h,
                    "suspicious_ips_24h": suspicious_ips,
                    "audit_entries_24h": audit_entries_24h,
                    "db_access_24h": db_access_24h,
                    "security_config": self.security_config
                }
                
        except Exception as e:
            logger.error(f"Error getting security stats: {e}")
            return {"error": str(e)}
    
    async def cleanup_old_logs(self, days_to_keep: int = 90):
        """Clean up old security logs"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            async with self.connection_pool.acquire() as conn:
                # Clean up old audit logs
                audit_deleted = await conn.execute("""
                    DELETE FROM security_audit_log 
                    WHERE timestamp < $1
                """, cutoff_date)
                
                # Clean up old failed login attempts
                failed_logins_deleted = await conn.execute("""
                    DELETE FROM failed_login_attempts 
                    WHERE attempt_time < $1
                """, cutoff_date)
                
                # Clean up old database access logs
                db_access_deleted = await conn.execute("""
                    DELETE FROM database_access_log 
                    WHERE timestamp < $1
                """, cutoff_date)
                
                logger.info(f"Cleaned up old security logs: {audit_deleted}, {failed_logins_deleted}, {db_access_deleted}")
                return {
                    "audit_logs_deleted": audit_deleted,
                    "failed_logins_deleted": failed_logins_deleted,
                    "db_access_deleted": db_access_deleted
                }
                
        except Exception as e:
            logger.error(f"Error cleaning up old logs: {e}")
            return {"error": str(e)}
    
    async def close(self):
        """Close database security connections"""
        try:
            if self.connection_pool:
                await self.connection_pool.close()
            if self.redis_client:
                await self.redis_client.close()
            logger.info("Database security connections closed")
        except Exception as e:
            logger.error(f"Error closing database security connections: {e}")
