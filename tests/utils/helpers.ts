import { Page, expect } from '@playwright/test';

/**
 * Common test helper functions
 */

/**
 * Wait for page to be fully loaded
 */
export async function waitForPageLoad(page: Page) {
  await page.waitForLoadState('networkidle');
  await page.waitForLoadState('domcontentloaded');
}

/**
 * Fill form fields from an object
 */
export async function fillForm(page: Page, formData: Record<string, string>) {
  for (const [field, value] of Object.entries(formData)) {
    const input = page.locator(`[name="${field}"], input[type="${field}"], #${field}`);
    await input.fill(value);
  }
}

/**
 * Wait for API response
 */
export async function waitForAPIResponse(
  page: Page,
  urlPattern: string | RegExp,
  timeout = 30000
) {
  return await page.waitForResponse(
    (response) => {
      const url = response.url();
      if (typeof urlPattern === 'string') {
        return url.includes(urlPattern);
      }
      return urlPattern.test(url);
    },
    { timeout }
  );
}

/**
 * Take screenshot with timestamp
 */
export async function takeScreenshot(page: Page, name: string) {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  await page.screenshot({
    path: `test-results/screenshots/${name}-${timestamp}.png`,
    fullPage: true,
  });
}

/**
 * Wait for element to be visible and stable
 */
export async function waitForStableElement(
  page: Page,
  selector: string,
  timeout = 10000
) {
  const element = page.locator(selector);
  await element.waitFor({ state: 'visible', timeout });
  // Wait a bit more for any animations
  await page.waitForTimeout(500);
  return element;
}

/**
 * Check if element exists without throwing
 */
export async function elementExists(page: Page, selector: string): Promise<boolean> {
  try {
    const element = page.locator(selector);
    await element.waitFor({ state: 'attached', timeout: 1000 });
    return true;
  } catch {
    return false;
  }
}

/**
 * Wait for notification to appear
 */
export async function waitForNotification(
  page: Page,
  message?: string,
  timeout = 5000
) {
  const notification = page.locator('.notification, .toast, .alert, [role="alert"]');
  await notification.waitFor({ state: 'visible', timeout });
  
  if (message) {
    await expect(notification).toContainText(message);
  }
  
  return notification;
}

/**
 * Clear all form fields
 */
export async function clearForm(page: Page) {
  const inputs = page.locator('input, textarea, select');
  const count = await inputs.count();
  
  for (let i = 0; i < count; i++) {
    await inputs.nth(i).clear();
  }
}

/**
 * Get text content safely
 */
export async function getTextContent(page: Page, selector: string): Promise<string> {
  try {
    const element = page.locator(selector);
    await element.waitFor({ state: 'visible', timeout: 5000 });
    return await element.textContent() || '';
  } catch {
    return '';
  }
}

/**
 * Check if user is logged in
 */
export async function isLoggedIn(page: Page): Promise<boolean> {
  try {
    // Check for common logged-in indicators
    const indicators = [
      '.user-profile',
      '.logout-button',
      '[data-user-id]',
      'text=Dashboard',
    ];
    
    for (const indicator of indicators) {
      if (await elementExists(page, indicator)) {
        return true;
      }
    }
    
    return false;
  } catch {
    return false;
  }
}

/**
 * Wait for API call to complete
 */
export async function waitForAPICall(
  page: Page,
  method: string,
  urlPattern: string | RegExp
) {
  return await page.waitForResponse(
    (response) => {
      const url = response.url();
      const matchesMethod = response.request().method() === method.toUpperCase();
      const matchesUrl = typeof urlPattern === 'string'
        ? url.includes(urlPattern)
        : urlPattern.test(url);
      return matchesMethod && matchesUrl;
    },
    { timeout: 30000 }
  );
}

