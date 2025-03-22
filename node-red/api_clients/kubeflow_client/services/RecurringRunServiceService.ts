/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { runtimeError } from '../models/runtimeError';
import type { v2beta1ListRecurringRunsResponse } from '../models/v2beta1ListRecurringRunsResponse';
import type { v2beta1RecurringRun } from '../models/v2beta1RecurringRun';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class RecurringRunServiceService {
    /**
     * Finds all recurring runs given experiment and namespace.
     * If experiment ID is not specified, find all recurring runs across all experiments.
     * @param pageToken A page token to request the next page of results. The token is acquired
     * from the nextPageToken field of the response from the previous
     * ListRecurringRuns call or can be omitted when fetching the first page.
     * @param pageSize The number of recurring runs to be listed per page. If there are more recurring runs
     * than this number, the response message will contain a nextPageToken field you can use
     * to fetch the next page.
     * @param sortBy Can be formatted as "field_name", "field_name asc" or "field_name desc".
     * Ascending by default.
     * @param namespace Optional input. The namespace the recurring runs belong to.
     * @param filter A url-encoded, JSON-serialized Filter protocol buffer (see
     * [filter.proto](https://github.com/kubeflow/pipelines/blob/master/backend/api/filter.proto)).
     * @param experimentId The ID of the experiment to be retrieved. If empty, list recurring runs across all experiments.
     * @returns v2beta1ListRecurringRunsResponse A successful response.
     * @returns runtimeError An unexpected error response.
     * @throws ApiError
     */
    public static recurringRunServiceListRecurringRuns(
        pageToken?: string,
        pageSize?: number,
        sortBy?: string,
        namespace?: string,
        filter?: string,
        experimentId?: string,
    ): CancelablePromise<v2beta1ListRecurringRunsResponse | runtimeError> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/apis/v2beta1/recurringruns',
            query: {
                'page_token': pageToken,
                'page_size': pageSize,
                'sort_by': sortBy,
                'namespace': namespace,
                'filter': filter,
                'experiment_id': experimentId,
            },
        });
    }
    /**
     * Creates a new recurring run in an experiment, given the experiment ID.
     * @param requestBody The recurring run to be created.
     * @returns v2beta1RecurringRun A successful response.
     * @returns runtimeError An unexpected error response.
     * @throws ApiError
     */
    public static recurringRunServiceCreateRecurringRun(
        requestBody: v2beta1RecurringRun,
    ): CancelablePromise<v2beta1RecurringRun | runtimeError> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/apis/v2beta1/recurringruns',
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Finds a specific recurring run by ID.
     * @param recurringRunId The ID of the recurring run to be retrieved.
     * @returns v2beta1RecurringRun A successful response.
     * @returns runtimeError An unexpected error response.
     * @throws ApiError
     */
    public static recurringRunServiceGetRecurringRun(
        recurringRunId: string,
    ): CancelablePromise<v2beta1RecurringRun | runtimeError> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/apis/v2beta1/recurringruns/{recurring_run_id}',
            path: {
                'recurring_run_id': recurringRunId,
            },
        });
    }
    /**
     * Deletes a recurring run.
     * @param recurringRunId The ID of the recurring run to be deleted.
     * @returns any A successful response.
     * @returns runtimeError An unexpected error response.
     * @throws ApiError
     */
    public static recurringRunServiceDeleteRecurringRun(
        recurringRunId: string,
    ): CancelablePromise<Record<string, any> | runtimeError> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/apis/v2beta1/recurringruns/{recurring_run_id}',
            path: {
                'recurring_run_id': recurringRunId,
            },
        });
    }
    /**
     * Stops a recurring run and all its associated runs. The recurring run is not deleted.
     * @param recurringRunId The ID of the recurring runs to be disabled.
     * @returns any A successful response.
     * @returns runtimeError An unexpected error response.
     * @throws ApiError
     */
    public static recurringRunServiceDisableRecurringRun(
        recurringRunId: string,
    ): CancelablePromise<Record<string, any> | runtimeError> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/apis/v2beta1/recurringruns/{recurring_run_id}:disable',
            path: {
                'recurring_run_id': recurringRunId,
            },
        });
    }
    /**
     * Restarts a recurring run that was previously stopped. All runs associated with the
     * recurring run will continue.
     * @param recurringRunId The ID of the recurring runs to be enabled.
     * @returns any A successful response.
     * @returns runtimeError An unexpected error response.
     * @throws ApiError
     */
    public static recurringRunServiceEnableRecurringRun(
        recurringRunId: string,
    ): CancelablePromise<Record<string, any> | runtimeError> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/apis/v2beta1/recurringruns/{recurring_run_id}:enable',
            path: {
                'recurring_run_id': recurringRunId,
            },
        });
    }
}
