/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $v2beta1ListExperimentsResponse = {
    properties: {
        experiments: {
            type: 'array',
            contains: {
                type: 'v2beta1Experiment',
            },
        },
        total_size: {
            type: 'number',
            description: `The number of experiments for the given query.`,
            format: 'int32',
        },
        next_page_token: {
            type: 'string',
            description: `The token to list the next page of experiments.`,
        },
    },
} as const;
