/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { v2beta1RecurringRun } from './v2beta1RecurringRun';
export type v2beta1ListRecurringRunsResponse = {
    /**
     * A list of recurring runs returned.
     */
    recurringRuns?: Array<v2beta1RecurringRun>;
    /**
     * The total number of recurring runs for the given query.
     */
    total_size?: number;
    /**
     * The token to list the next page of recurring runs.
     */
    next_page_token?: string;
};

