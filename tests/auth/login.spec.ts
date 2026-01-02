import { test, expect } from '../fixtures/auth';
import { testUsers } from '../fixtures/test-data';
import { waitForPageLoad, waitForNotification, elementExists } from '../utils/helpers';

/**
 * Authentication Tests - Login
 * Based on END_TO_END_AUTOMATION_TESTING_PLAN.md Section 2.3
 */

test.describe('User Login', () => {
  test('TC-AUTH-010: Login with valid credentials', async ({ page, baseURL }) => {
    // Navigate to homepage
    await page.goto(`${baseURL}/homepage.html`);
    await waitForPageLoad(page);
    
    // Click "Login" button
    const loginButton = page.locator('text=Login, a[href*="login"], button:has-text("Login")').first();
    await loginButton.click();
    
    // Wait for login page
    await page.waitForURL('**/login.html', { timeout: 10000 });
    
    // Enter valid email and password
    await page.fill('input[type="email"], input[name="email"], #email', testUsers.regular.email);
    await page.fill('input[type="password"], input[name="password"], #password', testUsers.regular.password);
    
    // Click "Sign In" button
    const submitButton = page.locator('button[type="submit"], button:has-text("Sign In"), button:has-text("Login")').first();
    await submitButton.click();
    
    // Verify successful login
    await page.waitForURL('**/dashboard.html', { timeout: 15000 });
    await expect(page).toHaveURL(/.*dashboard\.html/);
    
    // Verify user session created
    const token = await page.evaluate(() => localStorage.getItem('token') || sessionStorage.getItem('token'));
    expect(token).toBeTruthy();
  });

  test('TC-AUTH-011: Login with invalid email', async ({ page, baseURL }) => {
    await page.goto(`${baseURL}/login.html`);
    await waitForPageLoad(page);
    
    await page.fill('input[type="email"], input[name="email"]', 'invalid@example.com');
    await page.fill('input[type="password"], input[name="password"]', testUsers.regular.password);
    
    const submitButton = page.locator('button[type="submit"]').first();
    await submitButton.click();
    
    // Verify error message displayed
    await waitForNotification(page, /invalid|error|incorrect|not found/i, 5000);
  });

  test('TC-AUTH-012: Login with incorrect password', async ({ page, baseURL }) => {
    await page.goto(`${baseURL}/login.html`);
    await waitForPageLoad(page);
    
    await page.fill('input[type="email"], input[name="email"]', testUsers.regular.email);
    await page.fill('input[type="password"], input[name="password"]', 'WrongPassword123!');
    
    const submitButton = page.locator('button[type="submit"]').first();
    await submitButton.click();
    
    // Verify error message displayed
    await waitForNotification(page, /password|incorrect|invalid|error/i, 5000);
  });

  test('TC-AUTH-013: Login with unverified email', async ({ page, baseURL }) => {
    await page.goto(`${baseURL}/login.html`);
    await waitForPageLoad(page);
    
    // Use unverified test user (would need to be created in test setup)
    await page.fill('input[type="email"], input[name="email"]', 'unverified@craneintelligence.tech');
    await page.fill('input[type="password"], input[name="password"]', testUsers.regular.password);
    
    const submitButton = page.locator('button[type="submit"]').first();
    await submitButton.click();
    
    // Verify error message prompting verification
    await waitForNotification(page, /verify|verification|unverified/i, 5000);
  });

  test('TC-AUTH-014: Login with empty fields', async ({ page, baseURL }) => {
    await page.goto(`${baseURL}/login.html`);
    await waitForPageLoad(page);
    
    // Try to submit without filling fields
    const submitButton = page.locator('button[type="submit"]').first();
    await submitButton.click();
    
    // Verify field validation errors
    const emailInput = page.locator('input[type="email"], input[name="email"]').first();
    const passwordInput = page.locator('input[type="password"], input[name="password"]').first();
    
    // Check if HTML5 validation or custom validation is triggered
    const emailValid = await emailInput.evaluate((el: HTMLInputElement) => el.validity.valid);
    const passwordValid = await passwordInput.evaluate((el: HTMLInputElement) => el.validity.valid);
    
    // At least one should be invalid
    expect(emailValid || passwordValid).toBeFalsy();
  });
});

