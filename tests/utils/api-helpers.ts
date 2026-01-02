import { APIRequestContext, expect } from '@playwright/test';
import * as dotenv from 'dotenv';
import * as path from 'path';

dotenv.config({ path: path.resolve(__dirname, '../../.env.test') });

/**
 * API helper functions for testing
 */

export class APIHelpers {
  constructor(private request: APIRequestContext) {}

  /**
   * Get authentication token
   */
  async getAuthToken(email: string, password: string): Promise<string> {
    const response = await this.request.post(`${process.env.API_URL || 'https://dev.craneintelligence.tech/api/v1'}/auth/login`, {
      data: {
        email,
        password,
      },
    });

    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    return data.token || data.access_token;
  }

  /**
   * Make authenticated API request
   */
  async authenticatedRequest(
    method: string,
    endpoint: string,
    token: string,
    data?: any
  ) {
    const url = endpoint.startsWith('http') 
      ? endpoint 
      : `${process.env.API_URL || 'https://dev.craneintelligence.tech/api/v1'}${endpoint}`;

    return await this.request[method.toLowerCase()](url, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      data,
    });
  }

  /**
   * Create test user
   */
  async createTestUser(userData: {
    email: string;
    password: string;
    firstName: string;
    lastName: string;
    role: string;
  }) {
    const response = await this.request.post(
      `${process.env.API_URL || 'https://dev.craneintelligence.tech/api/v1'}/auth/register`,
      {
        data: userData,
      }
    );

    return await response.json();
  }

  /**
   * Create test FMV report
   */
  async createTestReport(token: string, reportData: any) {
    return await this.authenticatedRequest(
      'POST',
      '/fmv-reports/submit',
      token,
      reportData
    );
  }

  /**
   * Get user reports
   */
  async getUserReports(token: string, userId: number) {
    return await this.authenticatedRequest(
      'GET',
      `/fmv-reports/user/${userId}`,
      token
    );
  }

  /**
   * Update report status (admin only)
   */
  async updateReportStatus(token: string, reportId: number, status: string) {
    return await this.authenticatedRequest(
      'PUT',
      `/fmv-reports/${reportId}/status`,
      token,
      { status }
    );
  }
}

