/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { v2beta1Pipeline } from './v2beta1Pipeline';
export type v2beta1ListPipelinesResponse = {
    /**
     * Returned pipelines.
     */
    pipelines?: Array<v2beta1Pipeline>;
    /**
     * The total number of pipelines for the given query.
     */
    total_size?: number;
    /**
     * The token to list the next page of pipelines.
     * This token can be used on the next ListPipelinesRequest.
     */
    next_page_token?: string;
};

