/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Required input.
 * User setting to enable or disable the recurring run.
 * Only used for creation of recurring runs. Later updates use enable/disable API.
 *
 * - DISABLE: The recurring run won't schedule any run if disabled.
 */
export enum RecurringRunMode {
    MODE_UNSPECIFIED = 'MODE_UNSPECIFIED',
    ENABLE = 'ENABLE',
    DISABLE = 'DISABLE',
}
