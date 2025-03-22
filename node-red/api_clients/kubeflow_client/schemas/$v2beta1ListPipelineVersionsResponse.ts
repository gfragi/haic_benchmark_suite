/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $v2beta1ListPipelineVersionsResponse = {
    properties: {
        pipeline_versions: {
            type: 'array',
            contains: {
                type: 'v2beta1PipelineVersion',
            },
        },
        next_page_token: {
            type: 'string',
            description: `The token to list the next page of pipeline versions.`,
        },
        total_size: {
            type: 'number',
            description: `The total number of pipeline versions for the given query.`,
            format: 'int32',
        },
    },
} as const;
