# Crane Intelligence Test Suite

This directory contains end-to-end tests for the Crane Intelligence platform using Playwright.

## Structure

```
tests/
├── fixtures/          # Test fixtures and utilities
│   ├── auth.ts       # Authentication helpers
│   ├── database.ts    # Database utilities
│   └── test-data.ts  # Test data constants
├── utils/            # Helper functions
│   ├── helpers.ts    # Common page helpers
│   └── api-helpers.ts # API testing helpers
├── auth/             # Authentication tests
├── dashboard/         # Dashboard tests
├── valuation/         # Valuation terminal tests
├── fmv-reports/       # FMV report tests
├── payments/          # Payment tests
├── admin/             # Admin panel tests
└── api/               # API endpoint tests
```

## Running Tests

### Install Dependencies
```bash
npm install
```

### Run All Tests
```bash
npm test
```

### Run Tests in UI Mode
```bash
npm run test:ui
```

### Run Tests for Specific Environment
```bash
npm run test:dev    # Dev environment
npm run test:uat    # UAT environment
npm run test:prod   # Production environment
```

### Run Specific Test Tags
```bash
npm run test:smoke      # Smoke tests only
npm run test:critical   # Critical path tests
```

### Run in Debug Mode
```bash
npm run test:debug
```

### Run in Headed Mode (see browser)
```bash
npm run test:headed
```

## Test Organization

Tests are organized according to the `END_TO_END_AUTOMATION_TESTING_PLAN.md`:

- **Authentication Tests**: User registration, login, password reset
- **Dashboard Tests**: Dashboard functionality and statistics
- **Valuation Tests**: Valuation terminal and calculations
- **FMV Reports Tests**: Report generation and management
- **Payment Tests**: Payment processing and Stripe integration
- **Admin Tests**: Admin panel functionality
- **API Tests**: API endpoint testing

## Test Data

Test data is managed through:
- `tests/fixtures/test-data.ts` - Test data constants
- `tests/fixtures/database.ts` - Database seeding utilities

## Environment Configuration

Tests use environment variables from `.env.test`:
- `BASE_URL` - Base URL for the application
- `API_URL` - API endpoint URL
- `TEST_DATABASE_URL` - Test database connection string
- Test user credentials

## Writing New Tests

1. Create test file in appropriate directory
2. Import fixtures: `import { test, expect } from '../fixtures/auth';`
3. Use test data from `test-data.ts`
4. Follow naming convention: `TC-XXX-YYY: Test description`
5. Add appropriate tags (`@smoke`, `@critical`, etc.)

## CI/CD Integration

Tests run automatically in GitHub Actions:
- On push to `develop` branch
- On pull requests
- Before deployment to UAT/production

## Troubleshooting

### Tests Failing
1. Check that test environment is running
2. Verify database connection
3. Check test user credentials
4. Review test logs in `test-results/`

### Database Issues
1. Ensure test database is seeded
2. Check database connection in `.env.test`
3. Verify migrations are applied

### Authentication Issues
1. Check test user exists in database
2. Verify authentication state files
3. Check token expiration

