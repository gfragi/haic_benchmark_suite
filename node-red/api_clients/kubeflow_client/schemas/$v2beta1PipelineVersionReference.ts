/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $v2beta1PipelineVersionReference = {
    description: `Reference to an existing pipeline version.`,
    properties: {
        pipeline_id: {
            type: 'string',
            description: `Input. Required. Unique ID of the parent pipeline.`,
        },
        pipeline_version_id: {
            type: 'string',
            description: `Input. Optional. Unique ID of an existing pipeline version. If unset, the latest pipeline version is used.`,
        },
    },
} as const;
