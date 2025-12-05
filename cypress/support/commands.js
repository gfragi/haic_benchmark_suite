// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************

// Custom command to check if backend is healthy
Cypress.Commands.add('checkBackendHealth', () => {
  cy.request('GET', 'http://localhost:8000/meta/health')
    .its('status')
    .should('equal', 200)
})

// Custom command to wait for frontend to be ready
Cypress.Commands.add('waitForFrontend', () => {
  cy.visit('/', { timeout: 30000 })
  cy.contains('HAIC Evaluation Platform', { timeout: 30000 }).should('be.visible')
})

// Custom command to fill configuration form
Cypress.Commands.add('fillConfigurationForm', (data) => {
  if (data.application_name) {
    cy.get('input[label="Application Name"]').clear().type(data.application_name)
  }
  if (data.ai_model_name) {
    cy.get('input[label="AI Model Name"]').clear().type(data.ai_model_name)
  }
  if (data.ai_model_type) {
    cy.get('[label="AI Model Type"]').click()
    cy.get('.v-list-item').contains(data.ai_model_type).click()
  }
  if (data.metrics && data.metrics.length > 0) {
    cy.get('[label="Select Metrics Group"]').click()
    cy.get('.v-list-item').first().click()
  }
  if (data.description) {
    cy.get('textarea[label="Description"]').clear().type(data.description)
  }
})

// Custom command to submit configuration form
Cypress.Commands.add('submitConfiguration', () => {
  cy.get('button[type="submit"]').should('not.be.disabled').click()
})

// Custom command to verify success notification
Cypress.Commands.add('verifySuccessNotification', (message) => {
  if (message) {
    cy.contains(message).should('be.visible')
  }
})
