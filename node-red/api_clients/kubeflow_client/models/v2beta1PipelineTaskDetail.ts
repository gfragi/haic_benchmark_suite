/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { googlerpcStatus } from './googlerpcStatus';
import type { PipelineTaskDetailChildTask } from './PipelineTaskDetailChildTask';
import type { v2beta1ArtifactList } from './v2beta1ArtifactList';
import type { v2beta1PipelineTaskExecutorDetail } from './v2beta1PipelineTaskExecutorDetail';
import type { v2beta1RuntimeState } from './v2beta1RuntimeState';
import type { v2beta1RuntimeStatus } from './v2beta1RuntimeStatus';
/**
 * Runtime information of a task execution.
 */
export type v2beta1PipelineTaskDetail = {
    /**
     * ID of the parent run.
     */
    run_id?: string;
    /**
     * System-generated ID of a task.
     */
    task_id?: string;
    /**
     * User specified name of a task that is defined in
     * [Pipeline.spec][].
     */
    display_name?: string;
    /**
     * Creation time of a task.
     */
    create_time?: string;
    /**
     * Starting time of a task.
     */
    start_time?: string;
    /**
     * Completion time of a task.
     */
    end_time?: string;
    executor_detail?: v2beta1PipelineTaskExecutorDetail;
    state?: v2beta1RuntimeState;
    /**
     * Execution id of the corresponding entry in ML metadata store.
     */
    execution_id?: string;
    error?: googlerpcStatus;
    /**
     * Input artifacts of the task.
     */
    inputs?: Record<string, v2beta1ArtifactList>;
    /**
     * Output artifacts of the task.
     */
    outputs?: Record<string, v2beta1ArtifactList>;
    /**
     * ID of the parent task if the task is within a component scope.
     * Empty if the task is at the root level.
     */
    parent_task_id?: string;
    /**
     * A sequence of task statuses. This field keeps a record
     * of state transitions.
     */
    state_history?: Array<v2beta1RuntimeStatus>;
    /**
     * Name of the corresponding pod assigned by the orchestration engine.
     * Also known as node_id.
     */
    pod_name?: string;
    /**
     * Sequence of dependen tasks.
     */
    child_tasks?: Array<PipelineTaskDetailChildTask>;
};

