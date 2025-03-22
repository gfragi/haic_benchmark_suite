/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $ValidationData = {
    properties: {
        ai_detection_results: {
            type: 'any-of',
            contains: [{
                type: 'string',
            }, {
                type: 'null',
            }],
        },
        confidence_scores: {
            type: 'any-of',
            contains: [{
                type: 'dictionary',
                contains: {
                    type: 'number',
                },
            }, {
                type: 'null',
            }],
        },
        validation_results: {
            type: 'any-of',
            contains: [{
                type: 'string',
            }, {
                type: 'null',
            }],
        },
        confidence_level: {
            type: 'any-of',
            contains: [{
                type: 'number',
            }, {
                type: 'null',
            }],
        },
        processing_time_seconds: {
            type: 'any-of',
            contains: [{
                type: 'number',
            }, {
                type: 'null',
            }],
        },
        validation_time: {
            type: 'any-of',
            contains: [{
                type: 'string',
            }, {
                type: 'null',
            }],
        },
        system_metrics: {
            type: 'any-of',
            contains: [{
                type: 'SystemMetrics',
            }, {
                type: 'null',
            }],
        },
    },
} as const;
