function useConfigurationForm(props) {
  return {
    config: { value: { application_name: '', ai_model_name: '', ai_model_type: '', metrics: [], description: '' } },
    isEditMode: { value: false },
    formTitle: { value: 'Create Evaluation Configuration' },
    submitButtonText: { value: 'Next' },
    isFormValid: { value: false },
    availableModelTypes: ['Classification', 'Regression', 'Clustering', 'XAI', 'Swarm Learning', 'Active Learning', 'Other'],
    availableConfigTypes: ['specific', 'generic'],
    submitForm: () => Promise.resolve()
  };
}

module.exports = { useConfigurationForm };
