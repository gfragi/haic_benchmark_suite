/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $LogSchema = {
    properties: {
        session_id: {
            type: 'string',
            isRequired: true,
        },
        user_id: {
            type: 'string',
            isRequired: true,
        },
        ai_model_version: {
            type: 'any-of',
            contains: [{
                type: 'string',
            }, {
                type: 'null',
            }],
        },
        app_version: {
            type: 'string',
            isRequired: true,
        },
        start_time: {
            type: 'string',
            isRequired: true,
        },
        end_time: {
            type: 'string',
            isRequired: true,
        },
        interaction_data: {
            type: 'any-of',
            contains: [{
                type: 'InteractionData',
            }, {
                type: 'null',
            }],
        },
        retrain_events: {
            type: 'any-of',
            contains: [{
                type: 'array',
                contains: {
                    type: 'RetrainEvent',
                },
            }, {
                type: 'null',
            }],
        },
        performance_infrastructure: {
            type: 'any-of',
            contains: [{
                type: 'PerformanceInfrastructure',
            }, {
                type: 'null',
            }],
        },
        performance_logs: {
            type: 'any-of',
            contains: [{
                type: 'PerformanceLogs',
            }, {
                type: 'null',
            }],
        },
        ai_model_data: {
            type: 'any-of',
            contains: [{
                type: 'AIModelData',
            }, {
                type: 'null',
            }],
        },
    },
} as const;
