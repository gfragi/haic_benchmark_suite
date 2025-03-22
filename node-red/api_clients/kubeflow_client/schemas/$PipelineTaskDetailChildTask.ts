/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $PipelineTaskDetailChildTask = {
    description: `A dependent task that requires this one to succeed.
    Represented by either task_id or pod_name.`,
    properties: {
        task_id: {
            type: 'string',
            description: `System-generated ID of a task.`,
        },
        pod_name: {
            type: 'string',
            description: `Name of the corresponding pod assigned by the orchestration engine.
            Also known as node_id.`,
        },
    },
} as const;
