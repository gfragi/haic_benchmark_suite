/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { v2beta1PipelineTaskDetail } from './v2beta1PipelineTaskDetail';
/**
 * Runtime details of a run.
 */
export type v2beta1RunDetails = {
    /**
     * Pipeline context ID of a run.
     */
    pipeline_context_id?: string;
    /**
     * Pipeline run context ID of a run.
     */
    pipeline_run_context_id?: string;
    /**
     * Runtime details of the tasks that belong to the run.
     */
    task_details?: Array<v2beta1PipelineTaskDetail>;
};

