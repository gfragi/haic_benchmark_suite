/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { runtimeError } from '../models/runtimeError';
import type { v2beta1CreatePipelineAndVersionRequest } from '../models/v2beta1CreatePipelineAndVersionRequest';
import type { v2beta1ListPipelinesResponse } from '../models/v2beta1ListPipelinesResponse';
import type { v2beta1ListPipelineVersionsResponse } from '../models/v2beta1ListPipelineVersionsResponse';
import type { v2beta1Pipeline } from '../models/v2beta1Pipeline';
import type { v2beta1PipelineVersion } from '../models/v2beta1PipelineVersion';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class PipelineServiceService {
    /**
     * Finds all pipelines within a namespace.
     * @param namespace Optional input. Namespace for the pipelines.
     * @param pageToken A page token to request the results page.
     * @param pageSize The number of pipelines to be listed per page. If there are more pipelines
     * than this number, the response message will contain a valid value in the
     * nextPageToken field.
     * @param sortBy Sorting order in form of "field_name", "field_name asc" or "field_name desc".
     * Ascending by default.
     * @param filter A url-encoded, JSON-serialized filter protocol buffer (see
     * [filter.proto](https://github.com/kubeflow/pipelines/blob/master/backend/api/filter.proto)).
     * @returns v2beta1ListPipelinesResponse A successful response.
     * @returns runtimeError An unexpected error response.
     * @throws ApiError
     */
    public static pipelineServiceListPipelines(
        namespace?: string,
        pageToken?: string,
        pageSize?: number,
        sortBy?: string,
        filter?: string,
    ): CancelablePromise<v2beta1ListPipelinesResponse | runtimeError> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/apis/v2beta1/pipelines',
            query: {
                'namespace': namespace,
                'page_token': pageToken,
                'page_size': pageSize,
                'sort_by': sortBy,
                'filter': filter,
            },
        });
    }
    /**
     * Creates a pipeline.
     * @param requestBody Required input. Pipeline that needs to be created.
     * @returns v2beta1Pipeline A successful response.
     * @returns runtimeError An unexpected error response.
     * @throws ApiError
     */
    public static pipelineServiceCreatePipeline(
        requestBody: v2beta1Pipeline,
    ): CancelablePromise<v2beta1Pipeline | runtimeError> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/apis/v2beta1/pipelines',
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Creates a new pipeline and a new pipeline version in a single transaction.
     * @param requestBody
     * @returns v2beta1Pipeline A successful response.
     * @returns runtimeError An unexpected error response.
     * @throws ApiError
     */
    public static pipelineServiceCreatePipelineAndVersion(
        requestBody: v2beta1CreatePipelineAndVersionRequest,
    ): CancelablePromise<v2beta1Pipeline | runtimeError> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/apis/v2beta1/pipelines/create',
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Finds a specific pipeline by name and namespace.
     * @param name Required input. Name of the pipeline to be retrieved.
     * @param namespace Optional input. Namespace of the pipeline.
     * It could be empty if default namespaces needs to be used or if multi-user
     * support is turned off.
     * @returns v2beta1Pipeline A successful response.
     * @returns runtimeError An unexpected error response.
     * @throws ApiError
     */
    public static pipelineServiceGetPipelineByName(
        name: string,
        namespace?: string,
    ): CancelablePromise<v2beta1Pipeline | runtimeError> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/apis/v2beta1/pipelines/names/{name}',
            path: {
                'name': name,
            },
            query: {
                'namespace': namespace,
            },
        });
    }
    /**
     * Finds a specific pipeline by ID.
     * @param pipelineId Required input. The ID of the pipeline to be retrieved.
     * @returns v2beta1Pipeline A successful response.
     * @returns runtimeError An unexpected error response.
     * @throws ApiError
     */
    public static pipelineServiceGetPipeline(
        pipelineId: string,
    ): CancelablePromise<v2beta1Pipeline | runtimeError> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/apis/v2beta1/pipelines/{pipeline_id}',
            path: {
                'pipeline_id': pipelineId,
            },
        });
    }
    /**
     * Deletes an empty pipeline by ID. Returns error if the pipeline has pipeline versions.
     * @param pipelineId Required input. ID of the pipeline to be deleted.
     * @returns any A successful response.
     * @returns runtimeError An unexpected error response.
     * @throws ApiError
     */
    public static pipelineServiceDeletePipeline(
        pipelineId: string,
    ): CancelablePromise<Record<string, any> | runtimeError> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/apis/v2beta1/pipelines/{pipeline_id}',
            path: {
                'pipeline_id': pipelineId,
            },
        });
    }
    /**
     * Lists all pipeline versions of a given pipeline ID.
     * @param pipelineId Required input. ID of the parent pipeline.
     * @param pageToken A page token to request the results page.
     * @param pageSize The number of pipeline versions to be listed per page. If there are more pipeline
     * versions than this number, the response message will contain a valid value in the
     * nextPageToken field.
     * @param sortBy Sorting order in form of "field_name", "field_name asc" or "field_name desc".
     * Ascending by default.
     * @param filter A url-encoded, JSON-serialized filter protocol buffer (see
     * [filter.proto](https://github.com/kubeflow/pipelines/blob/master/backend/api/filter.proto)).
     * @returns v2beta1ListPipelineVersionsResponse A successful response.
     * @returns runtimeError An unexpected error response.
     * @throws ApiError
     */
    public static pipelineServiceListPipelineVersions(
        pipelineId: string,
        pageToken?: string,
        pageSize?: number,
        sortBy?: string,
        filter?: string,
    ): CancelablePromise<v2beta1ListPipelineVersionsResponse | runtimeError> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/apis/v2beta1/pipelines/{pipeline_id}/versions',
            path: {
                'pipeline_id': pipelineId,
            },
            query: {
                'page_token': pageToken,
                'page_size': pageSize,
                'sort_by': sortBy,
                'filter': filter,
            },
        });
    }
    /**
     * Adds a pipeline version to the specified pipeline ID.
     * @param pipelineId Required input. ID of the parent pipeline.
     * @param requestBody Required input. Pipeline version ID to be created.
     * @returns v2beta1PipelineVersion A successful response.
     * @returns runtimeError An unexpected error response.
     * @throws ApiError
     */
    public static pipelineServiceCreatePipelineVersion(
        pipelineId: string,
        requestBody: v2beta1PipelineVersion,
    ): CancelablePromise<v2beta1PipelineVersion | runtimeError> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/apis/v2beta1/pipelines/{pipeline_id}/versions',
            path: {
                'pipeline_id': pipelineId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Gets a pipeline version by pipeline version ID and pipeline ID.
     * @param pipelineId Required input. ID of the parent pipeline.
     * @param pipelineVersionId Required input. ID of the pipeline version to be retrieved.
     * @returns v2beta1PipelineVersion A successful response.
     * @returns runtimeError An unexpected error response.
     * @throws ApiError
     */
    public static pipelineServiceGetPipelineVersion(
        pipelineId: string,
        pipelineVersionId: string,
    ): CancelablePromise<v2beta1PipelineVersion | runtimeError> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/apis/v2beta1/pipelines/{pipeline_id}/versions/{pipeline_version_id}',
            path: {
                'pipeline_id': pipelineId,
                'pipeline_version_id': pipelineVersionId,
            },
        });
    }
    /**
     * Deletes a specific pipeline version by pipeline version ID and pipeline ID.
     * @param pipelineId Required input. ID of the parent pipeline.
     * @param pipelineVersionId Required input. The ID of the pipeline version to be deleted.
     * @returns any A successful response.
     * @returns runtimeError An unexpected error response.
     * @throws ApiError
     */
    public static pipelineServiceDeletePipelineVersion(
        pipelineId: string,
        pipelineVersionId: string,
    ): CancelablePromise<Record<string, any> | runtimeError> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/apis/v2beta1/pipelines/{pipeline_id}/versions/{pipeline_version_id}',
            path: {
                'pipeline_id': pipelineId,
                'pipeline_version_id': pipelineVersionId,
            },
        });
    }
}
