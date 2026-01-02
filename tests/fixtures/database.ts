import { Pool } from 'pg';
import * as dotenv from 'dotenv';
import * as path from 'path';

// Load test environment variables
dotenv.config({ path: path.resolve(__dirname, '../../.env.test') });

/**
 * Database connection pool for test database operations
 */
const pool = new Pool({
  host: process.env.TEST_DB_HOST || 'localhost',
  port: parseInt(process.env.TEST_DB_PORT || '5534'),
  database: process.env.TEST_DB_NAME || 'crane_intelligence_dev',
  user: process.env.TEST_DB_USER || 'crane_dev_user',
  password: process.env.TEST_DB_PASSWORD || 'crane_dev_password',
  max: 10,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 5000,
});

/**
 * Database utilities for test setup and teardown
 */
export class TestDatabase {
  private static pool = pool;

  /**
   * Execute a SQL query
   */
  static async query(text: string, params?: any[]) {
    return await this.pool.query(text, params);
  }

  /**
   * Seed test data
   */
  static async seedTestData() {
    // Create test users
    await this.query(`
      INSERT INTO users (email, password_hash, first_name, last_name, role, email_verified, created_at)
      VALUES 
        ('test@craneintelligence.tech', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqB5Z5K5Xe', 'Test', 'User', 'Crane Rental Company', true, NOW()),
        ('admin@craneintelligence.tech', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqB5Z5K5Xe', 'Admin', 'User', 'Admin', true, NOW())
      ON CONFLICT (email) DO NOTHING;
    `);
  }

  /**
   * Clean up test data
   */
  static async cleanupTestData() {
    // Delete test users and their data
    await this.query(`
      DELETE FROM users WHERE email IN ('test@craneintelligence.tech', 'admin@craneintelligence.tech');
    `);
  }

  /**
   * Reset database to clean state (use with caution)
   */
  static async resetDatabase() {
    // This should only be used in dev/test environments
    if (process.env.NODE_ENV === 'production') {
      throw new Error('Cannot reset database in production!');
    }
    
    // Truncate all tables (in correct order to respect foreign keys)
    await this.query(`
      TRUNCATE TABLE 
        fmv_reports,
        payments,
        notifications,
        consultations,
        equipment,
        users
      CASCADE;
    `);
  }

  /**
   * Get test user ID
   */
  static async getTestUserId(): Promise<number | null> {
    const result = await this.query(
      'SELECT id FROM users WHERE email = $1',
      ['test@craneintelligence.tech']
    );
    return result.rows[0]?.id || null;
  }

  /**
   * Get test admin ID
   */
  static async getTestAdminId(): Promise<number | null> {
    const result = await this.query(
      'SELECT id FROM users WHERE email = $1 AND role = $2',
      ['admin@craneintelligence.tech', 'Admin']
    );
    return result.rows[0]?.id || null;
  }

  /**
   * Close database connection
   */
  static async close() {
    await this.pool.end();
  }
}

export default TestDatabase;

