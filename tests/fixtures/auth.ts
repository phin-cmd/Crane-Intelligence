import { test as base, expect } from '@playwright/test';
import { Page } from '@playwright/test';

type AuthFixtures = {
  authenticatedPage: Page;
  adminPage: Page;
};

/**
 * Authentication fixtures for tests
 * Provides pre-authenticated pages for user and admin
 */
export const test = base.extend<AuthFixtures>({
  authenticatedPage: async ({ page, baseURL }, use) => {
    // Login as regular user
    await page.goto(`${baseURL}/login.html`);
    await page.fill('input[type="email"]', process.env.TEST_USER_EMAIL || 'test@craneintelligence.tech');
    await page.fill('input[type="password"]', process.env.TEST_USER_PASSWORD || 'TestPassword123!');
    await page.click('button[type="submit"]');
    
    // Wait for successful login
    await page.waitForURL('**/dashboard.html', { timeout: 10000 });
    await expect(page).toHaveURL(/.*dashboard\.html/);
    
    // Save authentication state
    await page.context().storageState({ path: 'tests/fixtures/auth-state-dev.json' });
    
    await use(page);
  },

  adminPage: async ({ page, baseURL }, use) => {
    // Login as admin
    await page.goto(`${baseURL}/admin/login.html`);
    await page.fill('input[type="email"]', process.env.TEST_ADMIN_EMAIL || 'admin@craneintelligence.tech');
    await page.fill('input[type="password"]', process.env.TEST_ADMIN_PASSWORD || 'AdminPassword123!');
    await page.click('button[type="submit"]');
    
    // Wait for admin dashboard
    await page.waitForURL('**/admin/dashboard.html', { timeout: 10000 });
    await expect(page).toHaveURL(/.*admin\/dashboard\.html/);
    
    // Save authentication state
    await page.context().storageState({ path: 'tests/fixtures/auth-state-admin.json' });
    
    await use(page);
  },
});

export { expect };

