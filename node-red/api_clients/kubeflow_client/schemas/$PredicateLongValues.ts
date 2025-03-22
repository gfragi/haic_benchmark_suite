/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $PredicateLongValues = {
    description: `List of long integers.`,
    properties: {
        values: {
            type: 'array',
            contains: {
                type: 'string',
                format: 'int64',
            },
        },
    },
} as const;
