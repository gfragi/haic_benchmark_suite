/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Reference to an existing pipeline version.
 */
export type v2beta1PipelineVersionReference = {
    /**
     * Input. Required. Unique ID of the parent pipeline.
     */
    pipeline_id?: string;
    /**
     * Input. Optional. Unique ID of an existing pipeline version. If unset, the latest pipeline version is used.
     */
    pipeline_version_id?: string;
};

