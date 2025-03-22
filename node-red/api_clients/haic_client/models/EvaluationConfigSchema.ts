/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type EvaluationConfigSchema = {
    id?: (number | null);
    application_name: string;
    ai_model_name: string;
    /**
     * One of: Classification, Regression, Clustering, XAI, Swarm Learning, Active Learning, Other
     */
    ai_model_type: string;
    metrics: Array<any>;
    evaluation_date?: string;
    description?: (string | null);
    /**
     * Either 'specific' or 'generic'
     */
    config_type: string;
    /**
     * Current status of the evaluation
     */
    evaluation_status?: string;
};

