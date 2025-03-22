/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $EvaluationConfigSchema = {
    properties: {
        id: {
            type: 'any-of',
            contains: [{
                type: 'number',
            }, {
                type: 'null',
            }],
        },
        application_name: {
            type: 'string',
            isRequired: true,
        },
        ai_model_name: {
            type: 'string',
            isRequired: true,
        },
        ai_model_type: {
            type: 'string',
            description: `One of: Classification, Regression, Clustering, XAI, Swarm Learning, Active Learning, Other`,
            isRequired: true,
        },
        metrics: {
            type: 'array',
            contains: {
                properties: {
                },
            },
            isRequired: true,
        },
        evaluation_date: {
            type: 'string',
            format: 'date-time',
        },
        description: {
            type: 'any-of',
            contains: [{
                type: 'string',
            }, {
                type: 'null',
            }],
        },
        config_type: {
            type: 'string',
            description: `Either 'specific' or 'generic'`,
            isRequired: true,
        },
        evaluation_status: {
            type: 'string',
            description: `Current status of the evaluation`,
        },
    },
} as const;
