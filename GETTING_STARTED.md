# Getting Started with Test Automation

## ✅ Setup Complete!

All components have been set up. Here's how to get started:

## 🚀 Quick Start

### 1. Install Playwright Browsers

```bash
cd /root/crane
npx playwright install --with-deps
```

This installs the browsers needed to run tests (Chrome, Firefox, Safari, etc.).

### 2. Verify Setup

```bash
./scripts/setup-verification.sh
```

This checks that everything is configured correctly.

### 3. Run Your First Test

```bash
# Run all tests
npm test

# Run in interactive UI mode (recommended for first time)
npm run test:ui

# Run specific test file
npx playwright test tests/auth/login.spec.ts
```

## 📝 Writing Tests

### Test Structure

Tests follow this structure:

```typescript
import { test, expect } from '../fixtures/auth';
import { testUsers } from '../fixtures/test-data';
import { waitForPageLoad } from '../utils/helpers';

test.describe('Feature Name', () => {
  test('TC-XXX-YYY: Test description', async ({ authenticatedPage, baseURL }) => {
    // Navigate to page
    await authenticatedPage.goto(`${baseURL}/page.html`);
    
    // Perform actions
    await authenticatedPage.click('button');
    
    // Verify results
    await expect(authenticatedPage.locator('.result')).toBeVisible();
  });
});
```

### Available Fixtures

- `page` - Regular page (not authenticated)
- `authenticatedPage` - Page with user logged in
- `adminPage` - Page with admin logged in
- `baseURL` - Base URL for current environment

### Test Data

Use test data from fixtures:

```typescript
import { testUsers, testCraneData, testReportData } from '../fixtures/test-data';

// Use test user
testUsers.regular.email
testUsers.regular.password

// Use test crane data
testCraneData.spotCheck.manufacturer
testCraneData.spotCheck.model
```

### Helper Functions

Use helper functions for common operations:

```typescript
import { 
  waitForPageLoad, 
  waitForNotification, 
  fillForm,
  elementExists 
} from '../utils/helpers';

// Wait for page to load
await waitForPageLoad(page);

// Wait for notification
await waitForNotification(page, /success/i);

// Fill form
await fillForm(page, {
  email: 'test@example.com',
  password: 'password123'
});
```

## 🎯 Test Organization

Tests are organized by feature area:

- `tests/auth/` - Authentication tests
- `tests/dashboard/` - Dashboard tests
- `tests/fmv-reports/` - FMV report tests
- `tests/valuation/` - Valuation terminal tests
- `tests/payments/` - Payment tests
- `tests/admin/` - Admin panel tests

## 🔧 Configuration

### Environment Variables

Edit `.env.test` to configure:
- Test database connection
- Test user credentials
- API endpoints

### Test Tags

Tag tests for selective execution:

```typescript
test('@smoke TC-001: Critical test', async ({ page }) => {
  // Test code
});

test('@critical TC-002: Important test', async ({ page }) => {
  // Test code
});
```

Run tagged tests:
```bash
npm run test:smoke      # Run @smoke tests
npm run test:critical   # Run @critical tests
```

## 📊 Test Execution

### Run All Tests

```bash
npm test
```

### Run by Environment

```bash
npm run test:dev    # Dev environment
npm run test:uat    # UAT environment
npm run test:prod   # Production environment
```

### Run in Debug Mode

```bash
npm run test:debug
```

This opens Playwright Inspector for step-by-step debugging.

### Run in UI Mode

```bash
npm run test:ui
```

This opens Playwright UI for interactive test execution.

## 📈 Test Reports

After running tests, view reports:

```bash
npm run test:report
```

This opens the HTML test report in your browser.

## 🐛 Troubleshooting

### Tests Fail to Run

1. **Check Playwright is installed**:
   ```bash
   npx playwright --version
   ```

2. **Install browsers**:
   ```bash
   npx playwright install --with-deps
   ```

3. **Check environment**:
   ```bash
   cat .env.test
   ```

### Tests Timeout

- Increase timeout in `playwright.config.ts`
- Check if application is running
- Verify network connectivity

### Selectors Not Found

- Use Playwright's codegen to find selectors:
  ```bash
  npm run test:codegen
  ```
- Check page structure in browser DevTools
- Use more flexible selectors (text, role, etc.)

## 📚 Next Steps

1. **Review Test Plan**: Read `END_TO_END_AUTOMATION_TESTING_PLAN.md`
2. **Write Tests**: Start with simple tests, build complexity
3. **Run Regularly**: Integrate into your workflow
4. **Maintain Tests**: Update tests as UI changes

## 💡 Tips

- Start with smoke tests (@smoke tag)
- Use page object pattern for complex pages
- Keep tests independent (no dependencies between tests)
- Use data-driven tests for multiple scenarios
- Clean up test data after each test

---

Happy Testing! 🎉

