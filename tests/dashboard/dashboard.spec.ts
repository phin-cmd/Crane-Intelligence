import { test, expect } from '../fixtures/auth';
import { waitForPageLoad, elementExists } from '../utils/helpers';

/**
 * Dashboard Tests
 * Based on END_TO_END_AUTOMATION_TESTING_PLAN.md Section 4
 */

test.describe('Dashboard', () => {
  test('TC-DASH-001: Access dashboard after login', async ({ authenticatedPage, baseURL }) => {
    // Should already be on dashboard from authenticatedPage fixture
    await expect(authenticatedPage).toHaveURL(/.*dashboard\.html/);
    
    // Verify dashboard loads correctly
    await waitForPageLoad(authenticatedPage);
    
    // Verify user information displayed
    const userInfo = authenticatedPage.locator('.user-profile, .user-info, [data-user]');
    await expect(userInfo.first()).toBeVisible({ timeout: 5000 });
  });

  test('TC-DASH-002: Dashboard without authentication', async ({ page, baseURL }) => {
    // Attempt to access dashboard URL directly without login
    await page.goto(`${baseURL}/dashboard.html`);
    
    // Should redirect to login page
    await page.waitForURL('**/login.html', { timeout: 10000 });
    await expect(page).toHaveURL(/.*login\.html/);
  });

  test('TC-DASH-003: View dashboard statistics', async ({ authenticatedPage, baseURL }) => {
    await authenticatedPage.goto(`${baseURL}/dashboard.html`);
    await waitForPageLoad(authenticatedPage);
    
    // Verify statistics displayed
    const stats = authenticatedPage.locator('.statistics, .stats, [data-stat], .metric');
    const count = await stats.count();
    
    // Should have at least some statistics
    expect(count).toBeGreaterThan(0);
    
    // Verify common statistics are present
    const statText = await authenticatedPage.textContent('body');
    expect(statText).toMatch(/valuation|report|spent|activity/i);
  });

  test('TC-DASH-005: Navigate to FMV Reports', async ({ authenticatedPage, baseURL }) => {
    await authenticatedPage.goto(`${baseURL}/dashboard.html`);
    await waitForPageLoad(authenticatedPage);
    
    // Click "FMV Report" link in header
    const fmvLink = authenticatedPage.locator('a:has-text("FMV"), a[href*="fmv"], a[href*="report"]').first();
    await fmvLink.click();
    
    // Verify navigation to FMV reports page
    await authenticatedPage.waitForURL('**/fmv-reports.html, **/my-reports.html', { timeout: 10000 });
  });

  test('TC-DASH-006: Navigate to Account Settings', async ({ authenticatedPage, baseURL }) => {
    await authenticatedPage.goto(`${baseURL}/dashboard.html`);
    await waitForPageLoad(authenticatedPage);
    
    // Click "Account Setting" link
    const accountLink = authenticatedPage.locator('a:has-text("Account"), a[href*="account"], a[href*="settings"]').first();
    await accountLink.click();
    
    // Verify navigation to account settings page
    await authenticatedPage.waitForURL('**/account-settings.html', { timeout: 10000 });
  });
});

