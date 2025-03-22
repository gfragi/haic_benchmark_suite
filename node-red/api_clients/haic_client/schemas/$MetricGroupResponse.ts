/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $MetricGroupResponse = {
    properties: {
        group_description: {
            type: 'any-of',
            contains: [{
                type: 'string',
            }, {
                type: 'null',
            }],
        },
        metrics: {
            type: 'array',
            contains: {
                type: 'MetricResponse',
            },
            isRequired: true,
        },
    },
} as const;
