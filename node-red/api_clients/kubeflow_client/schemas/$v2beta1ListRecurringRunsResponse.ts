/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $v2beta1ListRecurringRunsResponse = {
    properties: {
        recurringRuns: {
            type: 'array',
            contains: {
                type: 'v2beta1RecurringRun',
            },
        },
        total_size: {
            type: 'number',
            description: `The total number of recurring runs for the given query.`,
            format: 'int32',
        },
        next_page_token: {
            type: 'string',
            description: `The token to list the next page of recurring runs.`,
        },
    },
} as const;
