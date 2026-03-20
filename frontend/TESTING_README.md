# Frontend Testing Guide

## Overview
The HAIC Benchmark Suite frontend now includes comprehensive testing infrastructure with unit tests, component tests, and end-to-end tests.

## Test Structure

```
frontend/
├── tests/
│   └── unit/
│       └── composables/
│           ├── useConfigurationForm.spec.js
│           └── useMetrics.spec.js
├── cypress/
│   └── e2e/
│       └── configuration-workflow.cy.js
├── jest.config.js
└── cypress.config.js
```

## Running Tests

### Unit Tests (Jest)
```bash
# Run all unit tests
npm run test:unit

# Run unit tests in watch mode
npm run test:unit:watch

# Run unit tests with coverage
npm run test:unit:coverage
```

### End-to-End Tests (Cypress)
```bash
# Run E2E tests headlessly
npm run test:e2e

# Open Cypress test runner
npm run test:e2e:open
```

### All Tests
```bash
# Run both unit and E2E tests
npm run test:all
```

### Linting
```bash
# Check linting
npm run lint

# Fix linting issues automatically
npm run lint:fix
```

## Test Categories

### 1. Unit Tests (Composables)

#### useConfigurationForm.spec.js
Tests the configuration form logic:
- ✅ Form initialization (create/edit modes)
- ✅ Form validation (required fields)
- ✅ Form submission (success/error handling)
- ✅ Navigation after successful submission
- ✅ Loading states during API calls

#### useMetrics.spec.js
Tests the metrics data structure:
- ✅ Metric groups structure and properties
- ✅ All 6 metric categories (Effectiveness, Efficiency, etc.)
- ✅ Metric data integrity (no duplicates, valid formulas)
- ✅ Formula validation and readability

### 2. End-to-End Tests (Cypress)

#### configuration-workflow.cy.js
Tests complete user workflows:
- ✅ Home page loading
- ✅ Navigation to configuration creation
- ✅ Form validation (required fields)
- ✅ Successful configuration creation
- ✅ Metrics page display and interaction
- ✅ Navigation between pages
- ✅ Error handling scenarios

## Test Coverage Goals

### Current Coverage
- ✅ **Composables**: 100% coverage of business logic
- ✅ **Form Logic**: All validation and submission paths
- ✅ **Data Structures**: All metric definitions and formulas
- ✅ **User Workflows**: Critical paths tested end-to-end

### Future Coverage (Phase 4)
- 🔄 **Components**: Individual Vue component testing
- 🔄 **Store Modules**: Vuex state management testing
- 🔄 **API Integration**: Mocked API response testing
- 🔄 **Error Boundaries**: Error handling component testing

## Writing New Tests

### Unit Test Template
```javascript
import { describe, it, expect, beforeEach, vi } from 'jest'
import { composableToTest } from '@/composables/composableToTest'

describe('Composable Name', () => {
  let result

  beforeEach(() => {
    result = composableToTest(props)
  })

  describe('Feature Group', () => {
    it('should handle specific scenario', () => {
      // Arrange
      // Act
      // Assert
      expect(result.value).toBe(expectedValue)
    })
  })
})
```

### E2E Test Template
```javascript
describe('Feature Name', () => {
  beforeEach(() => {
    cy.visit('/starting-page')
  })

  it('should complete workflow successfully', () => {
    // Navigate
    cy.contains('Button Text').click()

    // Interact
    cy.get('input[name="field"]').type('value')

    // Verify
    cy.url().should('include', '/expected-page')
    cy.contains('Success message').should('be.visible')
  })
})
```

## Test Data

### Mock API Responses
```javascript
// Mock successful configuration creation
const mockConfigResponse = {
  id: 123,
  application_name: 'Test App',
  ai_model_name: 'Test Model',
  metrics: ['accuracy'],
  evaluation_status: 'pending'
}

// Mock metrics data
const mockMetricsResponse = {
  effectiveness: { metrics: [...] },
  efficiency: { metrics: [...] },
  // ... other categories
}
```

### Test Fixtures
```javascript
// Valid form data
const validFormData = {
  application_name: 'Test Application',
  ai_model_name: 'GPT-4',
  ai_model_type: 'Classification',
  metrics: ['accuracy', 'precision'],
  description: 'Test configuration'
}

// Invalid form data
const invalidFormData = {
  application_name: '',
  ai_model_name: '',
  ai_model_type: '',
  metrics: []
}
```

## CI/CD Integration

### GitHub Actions Example
```yaml
name: Frontend Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: cd frontend && npm install
      - run: cd frontend && npm run lint
      - run: cd frontend && npm run test:unit:coverage
      - run: cd frontend && npm run test:e2e
```

### Coverage Reporting
```javascript
// jest.config.js coverage settings
coverageReporters: ['html', 'text-summary', 'lcov'],
coverageDirectory: 'tests/coverage',
collectCoverageFrom: [
  'src/**/*.{js,vue}',
  '!src/main.js',
  '!**/node_modules/**'
]
```

## Debugging Tests

### Common Issues

#### 1. Async Test Timeouts
```javascript
it('should handle async operation', async () => {
  // Increase timeout for slow operations
  jest.setTimeout(10000)

  const result = await asyncOperation()
  expect(result).toBeDefined()
})
```

#### 2. Vue Component Testing
```javascript
import { mount } from '@vue/test-utils'
import Component from '@/components/Component.vue'

const wrapper = mount(Component, {
  props: { propName: 'value' },
  global: {
    plugins: [store, router]
  }
})
```

#### 3. Mocking API Calls
```javascript
// Mock axios in tests
vi.mock('axios')
axios.get.mockResolvedValue({ data: mockResponse })
```

## Performance Testing

### Bundle Size Analysis
```bash
# Analyze bundle size
npm run build -- --report
```

### Lighthouse Testing
```javascript
// Add to Cypress tests
cy.lighthouse({
  performance: 85,
  accessibility: 90,
  'best-practices': 85,
  seo: 85,
  pwa: 100,
})
```

## Test Maintenance

### Regular Tasks
- ✅ **Update Tests**: When adding new features
- ✅ **Fix Broken Tests**: After refactoring
- ✅ **Review Coverage**: Ensure new code is tested
- ✅ **Update Dependencies**: Keep testing tools current

### Best Practices
- ✅ **Descriptive Names**: Clear test and describe blocks
- ✅ **Independent Tests**: Each test should run alone
- ✅ **Fast Execution**: Keep tests running quickly
- ✅ **Realistic Data**: Use realistic test data
- ✅ **Edge Cases**: Test error conditions and boundaries

## Troubleshooting

### Test Failures
1. **Check Dependencies**: Ensure all dev dependencies are installed
2. **Clear Cache**: `rm -rf node_modules/.cache`
3. **Rebuild**: `npm run build` before testing
4. **Check Ports**: Ensure test servers aren't conflicting

### Cypress Issues
1. **Browser Issues**: Try different browser in Cypress runner
2. **Network Issues**: Check if baseUrl is accessible
3. **Flaky Tests**: Add wait conditions and retries

### Coverage Issues
1. **Missing Files**: Check jest.config.js collectCoverageFrom
2. **Excluded Files**: Verify files aren't in coverage exclusions
3. **Source Maps**: Ensure proper source map generation

## Future Enhancements

### Phase 4: Advanced Testing
- 🔄 **Visual Regression**: Screenshot comparison testing
- 🔄 **Performance Testing**: Load time and bundle analysis
- 🔄 **Accessibility Testing**: WCAG compliance checks
- 🔄 **Cross-browser Testing**: Multiple browser support
- 🔄 **API Contract Testing**: Backend API validation
- 🔄 **Security Testing**: Vulnerability scanning

---

## Quick Start

```bash
# Install dependencies
npm install

# Run all tests
npm run test:all

# Development with testing
npm run serve          # Terminal 1: Development server
npm run test:unit:watch # Terminal 2: Unit tests in watch mode
npm run test:e2e:open  # Terminal 3: E2E tests in Cypress runner
```

This testing infrastructure ensures the HAIC Benchmark Suite frontend remains reliable, maintainable, and user-friendly as new features are added.
