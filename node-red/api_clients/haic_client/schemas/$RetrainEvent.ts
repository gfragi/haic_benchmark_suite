/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $RetrainEvent = {
    properties: {
        retraining_time: {
            type: 'any-of',
            contains: [{
                type: 'string',
            }, {
                type: 'null',
            }],
        },
        initial_metrics: {
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
        post_retraining_metrics: {
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
        retraining_details: {
            type: 'any-of',
            contains: [{
                type: 'RetrainingDetails',
            }, {
                type: 'null',
            }],
        },
    },
} as const;
