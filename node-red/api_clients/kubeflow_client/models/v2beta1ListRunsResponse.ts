/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { v2beta1Run } from './v2beta1Run';
export type v2beta1ListRunsResponse = {
    /**
     * List of retrieved runs.
     */
    runs?: Array<v2beta1Run>;
    /**
     * The total number of runs for the given query.
     */
    total_size?: number;
    /**
     * The token to list the next page of runs.
     */
    next_page_token?: string;
};

