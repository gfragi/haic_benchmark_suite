/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { runtimeError } from '../models/runtimeError';
import type { v2beta1ListRunsResponse } from '../models/v2beta1ListRunsResponse';
import type { v2beta1ReadArtifactResponse } from '../models/v2beta1ReadArtifactResponse';
import type { v2beta1Run } from '../models/v2beta1Run';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class RunServiceService {
    /**
     * Finds all runs in an experiment given by experiment ID.
     * If experiment id is not specified, finds all runs across all experiments.
     * @param namespace Optional input field. Filters based on the namespace.
     * @param experimentId The ID of the parent experiment. If empty, response includes runs across all experiments.
     * @param pageToken A page token to request the next page of results. The token is acquired
     * from the nextPageToken field of the response from the previous
     * ListRuns call or can be omitted when fetching the first page.
     * @param pageSize The number of runs to be listed per page. If there are more runs than this
     * number, the response message will contain a nextPageToken field you can use
     * to fetch the next page.
     * @param sortBy Can be format of "field_name", "field_name asc" or "field_name desc"
     * (Example, "name asc" or "id desc"). Ascending by default.
     * @param filter A url-encoded, JSON-serialized Filter protocol buffer (see
     * [filter.proto](https://github.com/kubeflow/pipelines/blob/master/backend/api/filter.proto)).
     * @returns v2beta1ListRunsResponse A successful response.
     * @returns runtimeError An unexpected error response.
     * @throws ApiError
     */
    public static runServiceListRuns(
        namespace?: string,
        experimentId?: string,
        pageToken?: string,
        pageSize?: number,
        sortBy?: string,
        filter?: string,
    ): CancelablePromise<v2beta1ListRunsResponse | runtimeError> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/apis/v2beta1/runs',
            query: {
                'namespace': namespace,
                'experiment_id': experimentId,
                'page_token': pageToken,
                'page_size': pageSize,
                'sort_by': sortBy,
                'filter': filter,
            },
        });
    }
    /**
     * Creates a new run in an experiment specified by experiment ID.
     * If experiment ID is not specified, the run is created in the default experiment.
     * @param requestBody Run to be created.
     * @param experimentId The ID of the parent experiment.
     * @returns v2beta1Run A successful response.
     * @returns runtimeError An unexpected error response.
     * @throws ApiError
     */
    public static runServiceCreateRun(
        requestBody: v2beta1Run,
        experimentId?: string,
    ): CancelablePromise<v2beta1Run | runtimeError> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/apis/v2beta1/runs',
            query: {
                'experiment_id': experimentId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Finds a specific run by ID.
     * @param runId The ID of the run to be retrieved.
     * @param experimentId The ID of the parent experiment.
     * @returns v2beta1Run A successful response.
     * @returns runtimeError An unexpected error response.
     * @throws ApiError
     */
    public static runServiceGetRun(
        runId: string,
        experimentId?: string,
    ): CancelablePromise<v2beta1Run | runtimeError> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/apis/v2beta1/runs/{run_id}',
            path: {
                'run_id': runId,
            },
            query: {
                'experiment_id': experimentId,
            },
        });
    }
    /**
     * Deletes a run in an experiment given by run ID and experiment ID.
     * @param runId The ID of the run to be deleted.
     * @param experimentId The ID of the parent experiment.
     * @returns any A successful response.
     * @returns runtimeError An unexpected error response.
     * @throws ApiError
     */
    public static runServiceDeleteRun(
        runId: string,
        experimentId?: string,
    ): CancelablePromise<Record<string, any> | runtimeError> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/apis/v2beta1/runs/{run_id}',
            path: {
                'run_id': runId,
            },
            query: {
                'experiment_id': experimentId,
            },
        });
    }
    /**
     * Finds artifact data in a run.
     * @param runId ID of the run.
     * @param nodeId ID of the running node.
     * @param artifactName Name of the artifact.
     * @param experimentId The ID of the parent experiment.
     * @returns v2beta1ReadArtifactResponse A successful response.
     * @returns runtimeError An unexpected error response.
     * @throws ApiError
     */
    public static runServiceReadArtifact(
        runId: string,
        nodeId: string,
        artifactName: string,
        experimentId?: string,
    ): CancelablePromise<v2beta1ReadArtifactResponse | runtimeError> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/apis/v2beta1/runs/{run_id}/nodes/{node_id}/artifacts/{artifact_name}:read',
            path: {
                'run_id': runId,
                'node_id': nodeId,
                'artifact_name': artifactName,
            },
            query: {
                'experiment_id': experimentId,
            },
        });
    }
    /**
     * Archives a run in an experiment given by run ID and experiment ID.
     * @param runId The ID of the run to be archived.
     * @returns any A successful response.
     * @returns runtimeError An unexpected error response.
     * @throws ApiError
     */
    public static runServiceArchiveRun(
        runId: string,
    ): CancelablePromise<Record<string, any> | runtimeError> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/apis/v2beta1/runs/{run_id}:archive',
            path: {
                'run_id': runId,
            },
        });
    }
    /**
     * Re-initiates a failed or terminated run.
     * @param runId The ID of the run to be retried.
     * @returns any A successful response.
     * @returns runtimeError An unexpected error response.
     * @throws ApiError
     */
    public static runServiceRetryRun(
        runId: string,
    ): CancelablePromise<Record<string, any> | runtimeError> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/apis/v2beta1/runs/{run_id}:retry',
            path: {
                'run_id': runId,
            },
        });
    }
    /**
     * Terminates an active run.
     * @param runId The ID of the run to be terminated.
     * @returns any A successful response.
     * @returns runtimeError An unexpected error response.
     * @throws ApiError
     */
    public static runServiceTerminateRun(
        runId: string,
    ): CancelablePromise<Record<string, any> | runtimeError> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/apis/v2beta1/runs/{run_id}:terminate',
            path: {
                'run_id': runId,
            },
        });
    }
    /**
     * Restores an archived run in an experiment given by run ID and experiment ID.
     * @param runId The ID of the run to be restored.
     * @returns any A successful response.
     * @returns runtimeError An unexpected error response.
     * @throws ApiError
     */
    public static runServiceUnarchiveRun(
        runId: string,
    ): CancelablePromise<Record<string, any> | runtimeError> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/apis/v2beta1/runs/{run_id}:unarchive',
            path: {
                'run_id': runId,
            },
        });
    }
}
