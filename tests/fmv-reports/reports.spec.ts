import { test, expect } from '../fixtures/auth';
import { testCraneData, testReportData } from '../fixtures/test-data';
import { waitForPageLoad, waitForNotification } from '../utils/helpers';

/**
 * FMV Reports Tests
 * Based on END_TO_END_AUTOMATION_TESTING_PLAN.md Section 6
 */

test.describe('FMV Reports', () => {
  test('TC-FMV-001: Submit Spot Check report request', async ({ authenticatedPage, baseURL }) => {
    await authenticatedPage.goto(`${baseURL}/generate-report.html`);
    await waitForPageLoad(authenticatedPage);
    
    // Select "Spot Check" tier
    const spotCheckOption = authenticatedPage.locator('text=Spot Check, [data-tier="spot"], input[value="spot"]').first();
    await spotCheckOption.click();
    
    // Fill in crane information
    await authenticatedPage.fill('input[name="manufacturer"], #manufacturer', testCraneData.spotCheck.manufacturer);
    await authenticatedPage.fill('input[name="model"], #model', testCraneData.spotCheck.model);
    await authenticatedPage.fill('input[name="year"], #year', testCraneData.spotCheck.year.toString());
    await authenticatedPage.fill('input[name="capacity"], #capacity', testCraneData.spotCheck.capacity.toString());
    
    // Submit request
    const submitButton = authenticatedPage.locator('button[type="submit"], button:has-text("Submit")').first();
    await submitButton.click();
    
    // Verify redirect to payment page or confirmation
    await authenticatedPage.waitForURL('**/payment**, **/checkout**, **/confirm**', { timeout: 15000 });
  });

  test('TC-FMV-004: Report submission validation', async ({ authenticatedPage, baseURL }) => {
    await authenticatedPage.goto(`${baseURL}/generate-report.html`);
    await waitForPageLoad(authenticatedPage);
    
    // Attempt submission with missing required fields
    const submitButton = authenticatedPage.locator('button[type="submit"]').first();
    await submitButton.click();
    
    // Verify validation errors displayed
    const errorMessages = authenticatedPage.locator('.error, .validation-error, [role="alert"]');
    const errorCount = await errorMessages.count();
    
    // Should have at least one validation error
    expect(errorCount).toBeGreaterThan(0);
  });

  test('TC-FMV-009: View user\'s FMV reports', async ({ authenticatedPage, baseURL }) => {
    await authenticatedPage.goto(`${baseURL}/fmv-reports.html, ${baseURL}/my-reports.html`);
    await waitForPageLoad(authenticatedPage);
    
    // Verify reports page loads
    await expect(authenticatedPage).toHaveURL(/.*(fmv-reports|my-reports)\.html/);
    
    // Verify reports are displayed (even if empty)
    const reportsContainer = authenticatedPage.locator('.reports, .report-list, [data-reports]');
    await expect(reportsContainer.first()).toBeVisible({ timeout: 5000 });
  });

  test('TC-FMV-010: Filter reports by status', async ({ authenticatedPage, baseURL }) => {
    await authenticatedPage.goto(`${baseURL}/fmv-reports.html`);
    await waitForPageLoad(authenticatedPage);
    
    // Look for filter buttons
    const filterButtons = authenticatedPage.locator('.filter-btn, button:has-text("Pending"), button:has-text("Completed")');
    const filterCount = await filterButtons.count();
    
    if (filterCount > 0) {
      // Click on a filter
      await filterButtons.first().click();
      
      // Wait for filter to apply
      await authenticatedPage.waitForTimeout(1000);
      
      // Verify filter is active
      const activeFilter = authenticatedPage.locator('.filter-btn.active, button.active');
      await expect(activeFilter.first()).toBeVisible({ timeout: 2000 });
    }
  });
});

