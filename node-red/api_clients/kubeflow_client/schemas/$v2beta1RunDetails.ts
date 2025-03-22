/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $v2beta1RunDetails = {
    description: `Runtime details of a run.`,
    properties: {
        pipeline_context_id: {
            type: 'string',
            description: `Pipeline context ID of a run.`,
            format: 'int64',
        },
        pipeline_run_context_id: {
            type: 'string',
            description: `Pipeline run context ID of a run.`,
            format: 'int64',
        },
        task_details: {
            type: 'array',
            contains: {
                type: 'v2beta1PipelineTaskDetail',
            },
        },
    },
} as const;
