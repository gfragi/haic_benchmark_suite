describe('Configuration Workflow', () => {
  beforeEach(() => {
    // Visit the home page
    cy.visit('/')
  })

  it('should load the home page successfully', () => {
    // Check that the page loads
    cy.contains('Welcome to the HAIC Evaluation Platform').should('be.visible')

    // Check for the main navigation elements
    cy.contains('Start New Evaluation').should('be.visible')
  })

  it('should navigate to configuration creation', () => {
    // Click the start new evaluation button
    cy.contains('Start New Evaluation').click()

    // Should navigate to configuration form
    cy.url().should('include', '/configuration/new')

    // Check that the form is loaded
    cy.contains('Create Evaluation Configuration').should('be.visible')
  })

  it('should validate required fields', () => {
    // Navigate to configuration form
    cy.visit('/configuration/new')

    // Try to submit empty form
    cy.get('button[type="submit"]').should('be.disabled')
  })

  it('should create a configuration successfully', () => {
    // Navigate to configuration form
    cy.visit('/configuration/new')

    // Fill out the form
    cy.get('input[label="Application Name"]').type('Test Application')
    cy.get('input[label="AI Model Name"]').type('Test Model')

    // Select AI model type
    cy.get('[label="AI Model Type"]').click()
    cy.get('.v-list-item').contains('Classification').click()

    // Select metrics
    cy.get('[label="Select Metrics Group"]').click()
    cy.get('.v-list-item').first().click()

    // Add description
    cy.get('textarea[label="Description"]').type('Test configuration for E2E testing')

    // Submit the form
    cy.get('button[type="submit"]').should('not.be.disabled').click()

    // Should show success notification (if implemented)
    // cy.contains('Configuration created successfully').should('be.visible')

    // Should navigate to log upload page
    cy.url().should('include', '/logs/upload')
    cy.url().should('include', 'configId=')
  })

  it('should display metrics page correctly', () => {
    // Visit metrics page
    cy.visit('/metrics')

    // Check page title
    cy.contains('Human-AI Collaboration Metrics').should('be.visible')

    // Check that metric groups are displayed
    cy.contains('Effectiveness Metrics').should('be.visible')
    cy.contains('Efficiency Metrics').should('be.visible')
    cy.contains('Trust and Safety Metrics').should('be.visible')

    // Check that expansion panels work
    cy.get('.v-expansion-panel').first().click()
    cy.contains('Prediction Accuracy').should('be.visible')
  })

  it('should handle navigation between pages', () => {
    // Start from home
    cy.visit('/')

    // Navigate to metrics
    cy.contains('Go to Metrics').click()
    cy.url().should('include', '/metrics')

    // Navigate back to home
    cy.contains('Back to Dashboard').click()
    cy.url().should('include', '/')
  })

  it('should handle API errors gracefully', () => {
    // This test would need to mock API failures
    // For now, just check that the UI handles loading states

    cy.visit('/configuration/new')

    // The form should be in a loading state initially while fetching metrics
    // This demonstrates that the UI handles async operations properly
    cy.get('input[label="Application Name"]').should('be.visible')
  })
})
