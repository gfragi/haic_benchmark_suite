/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { v2beta1PipelineVersion } from './v2beta1PipelineVersion';
export type v2beta1ListPipelineVersionsResponse = {
    /**
     * Returned pipeline versions.
     */
    pipeline_versions?: Array<v2beta1PipelineVersion>;
    /**
     * The token to list the next page of pipeline versions.
     */
    next_page_token?: string;
    /**
     * The total number of pipeline versions for the given query.
     */
    total_size?: number;
};

