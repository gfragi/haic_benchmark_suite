/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * A dependent task that requires this one to succeed.
 * Represented by either task_id or pod_name.
 */
export type PipelineTaskDetailChildTask = {
    /**
     * System-generated ID of a task.
     */
    task_id?: string;
    /**
     * Name of the corresponding pod assigned by the orchestration engine.
     * Also known as node_id.
     */
    pod_name?: string;
};

