/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { googlerpcStatus } from './googlerpcStatus';
import type { v2beta1RuntimeState } from './v2beta1RuntimeState';
/**
 * Timestamped representation of a runtime state with an optional error.
 */
export type v2beta1RuntimeStatus = {
    /**
     * Update time of this state.
     */
    update_time?: string;
    state?: v2beta1RuntimeState;
    error?: googlerpcStatus;
};

