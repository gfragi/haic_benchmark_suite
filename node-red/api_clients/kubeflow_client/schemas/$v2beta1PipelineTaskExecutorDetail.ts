/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $v2beta1PipelineTaskExecutorDetail = {
    description: `Runtime information of a pipeline task executor.`,
    properties: {
        main_job: {
            type: 'string',
            description: `The name of the job for the main container execution.`,
        },
        pre_caching_check_job: {
            type: 'string',
            description: `The name of the job for the pre-caching-check container
            execution. This job will be available if the
            Run.pipeline_spec specifies the \`pre_caching_check\` hook in
            the lifecycle events.`,
        },
        failed_main_jobs: {
            type: 'array',
            contains: {
                type: 'string',
            },
        },
        failed_pre_caching_check_jobs: {
            type: 'array',
            contains: {
                type: 'string',
            },
        },
    },
} as const;
