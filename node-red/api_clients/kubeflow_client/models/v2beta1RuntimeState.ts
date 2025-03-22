/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Describes the runtime state of an entity.
 *
 * - RUNTIME_STATE_UNSPECIFIED: Default value. This value is not used.
 * - PENDING: Service is preparing to execute an entity.
 * - RUNNING: Entity execution is in progress.
 * - SUCCEEDED: Entity completed successfully.
 * - SKIPPED: Entity has been skipped. For example, due to caching.
 * - FAILED: Entity execution has failed.
 * - CANCELING: Entity is being canceled. From this state, an entity may only
 * change its state to SUCCEEDED, FAILED or CANCELED.
 * - CANCELED: Entity has been canceled.
 * - PAUSED: Entity has been paused. It can be resumed.
 */
export enum v2beta1RuntimeState {
    RUNTIME_STATE_UNSPECIFIED = 'RUNTIME_STATE_UNSPECIFIED',
    PENDING = 'PENDING',
    RUNNING = 'RUNNING',
    SUCCEEDED = 'SUCCEEDED',
    SKIPPED = 'SKIPPED',
    FAILED = 'FAILED',
    CANCELING = 'CANCELING',
    CANCELED = 'CANCELED',
    PAUSED = 'PAUSED',
}
