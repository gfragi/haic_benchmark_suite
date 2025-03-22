/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Runtime information of a pipeline task executor.
 */
export type v2beta1PipelineTaskExecutorDetail = {
    /**
     * The name of the job for the main container execution.
     */
    main_job?: string;
    /**
     * The name of the job for the pre-caching-check container
     * execution. This job will be available if the
     * Run.pipeline_spec specifies the `pre_caching_check` hook in
     * the lifecycle events.
     */
    pre_caching_check_job?: string;
    /**
     * The names of the previously failed job for the main container
     * executions. The list includes the all attempts in chronological order.
     */
    failed_main_jobs?: Array<string>;
    /**
     * The names of the previously failed job for the
     * pre-caching-check container executions. This job will be available if the
     * Run.pipeline_spec specifies the `pre_caching_check` hook in
     * the lifecycle events.
     * The list includes the all attempts in chronological order.
     */
    failed_pre_caching_check_jobs?: Array<string>;
};

