/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $PredicateIntValues = {
    description: `List of integers.`,
    properties: {
        values: {
            type: 'array',
            contains: {
                type: 'number',
                format: 'int32',
            },
        },
    },
} as const;
