/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $v2beta1ListPipelinesResponse = {
    properties: {
        pipelines: {
            type: 'array',
            contains: {
                type: 'v2beta1Pipeline',
            },
        },
        total_size: {
            type: 'number',
            description: `The total number of pipelines for the given query.`,
            format: 'int32',
        },
        next_page_token: {
            type: 'string',
            description: `The token to list the next page of pipelines.
            This token can be used on the next ListPipelinesRequest.`,
        },
    },
} as const;
