/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $v2beta1PipelineTaskDetail = {
    description: `Runtime information of a task execution.`,
    properties: {
        run_id: {
            type: 'string',
            description: `ID of the parent run.`,
        },
        task_id: {
            type: 'string',
            description: `System-generated ID of a task.`,
        },
        display_name: {
            type: 'string',
            description: `User specified name of a task that is defined in
            [Pipeline.spec][].`,
        },
        create_time: {
            type: 'string',
            description: `Creation time of a task.`,
            format: 'date-time',
        },
        start_time: {
            type: 'string',
            description: `Starting time of a task.`,
            format: 'date-time',
        },
        end_time: {
            type: 'string',
            description: `Completion time of a task.`,
            format: 'date-time',
        },
        executor_detail: {
            type: 'v2beta1PipelineTaskExecutorDetail',
        },
        state: {
            type: 'v2beta1RuntimeState',
        },
        execution_id: {
            type: 'string',
            description: `Execution id of the corresponding entry in ML metadata store.`,
            format: 'int64',
        },
        error: {
            type: 'googlerpcStatus',
        },
        inputs: {
            type: 'dictionary',
            contains: {
                type: 'v2beta1ArtifactList',
            },
        },
        outputs: {
            type: 'dictionary',
            contains: {
                type: 'v2beta1ArtifactList',
            },
        },
        parent_task_id: {
            type: 'string',
            description: `ID of the parent task if the task is within a component scope.
            Empty if the task is at the root level.`,
        },
        state_history: {
            type: 'array',
            contains: {
                type: 'v2beta1RuntimeStatus',
            },
        },
        pod_name: {
            type: 'string',
            description: `Name of the corresponding pod assigned by the orchestration engine.
            Also known as node_id.`,
        },
        child_tasks: {
            type: 'array',
            contains: {
                type: 'PipelineTaskDetailChildTask',
            },
        },
    },
} as const;
