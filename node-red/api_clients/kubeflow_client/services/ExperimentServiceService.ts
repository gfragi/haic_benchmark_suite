/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { runtimeError } from '../models/runtimeError';
import type { v2beta1Experiment } from '../models/v2beta1Experiment';
import type { v2beta1ListExperimentsResponse } from '../models/v2beta1ListExperimentsResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class ExperimentServiceService {
    /**
     * Finds all experiments. Supports pagination, and sorting on certain fields.
     * @param pageToken A page token to request the next page of results. The token is acquried
     * from the nextPageToken field of the response from the previous
     * ListExperiments call or can be omitted when fetching the first page.
     * @param pageSize The number of experiments to be listed per page. If there are more
     * experiments than this number, the response message will contain a
     * nextPageToken field you can use to fetch the next page.
     * @param sortBy Can be format of "field_name", "field_name asc" or "field_name desc"
     * Ascending by default.
     * @param filter A url-encoded, JSON-serialized Filter protocol buffer (see
     * [filter.proto](https://github.com/kubeflow/pipelines/blob/master/backend/api/v2beta1/api/filter.proto)).
     * @param namespace Which namespace to filter the experiments on.
     * @returns v2beta1ListExperimentsResponse A successful response.
     * @returns runtimeError An unexpected error response.
     * @throws ApiError
     */
    public static experimentServiceListExperiments(
        pageToken?: string,
        pageSize?: number,
        sortBy?: string,
        filter?: string,
        namespace?: string,
    ): CancelablePromise<v2beta1ListExperimentsResponse | runtimeError> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/apis/v2beta1/experiments',
            query: {
                'page_token': pageToken,
                'page_size': pageSize,
                'sort_by': sortBy,
                'filter': filter,
                'namespace': namespace,
            },
        });
    }
    /**
     * Creates a new experiment.
     * @param requestBody The experiment to be created.
     * @returns v2beta1Experiment A successful response.
     * @returns runtimeError An unexpected error response.
     * @throws ApiError
     */
    public static experimentServiceCreateExperiment(
        requestBody: v2beta1Experiment,
    ): CancelablePromise<v2beta1Experiment | runtimeError> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/apis/v2beta1/experiments',
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Finds a specific experiment by ID.
     * @param experimentId The ID of the experiment to be retrieved.
     * @returns v2beta1Experiment A successful response.
     * @returns runtimeError An unexpected error response.
     * @throws ApiError
     */
    public static experimentServiceGetExperiment(
        experimentId: string,
    ): CancelablePromise<v2beta1Experiment | runtimeError> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/apis/v2beta1/experiments/{experiment_id}',
            path: {
                'experiment_id': experimentId,
            },
        });
    }
    /**
     * Deletes an experiment without deleting the experiment's runs and recurring
     * runs. To avoid unexpected behaviors, delete an experiment's runs and recurring
     * runs before deleting the experiment.
     * @param experimentId The ID of the experiment to be deleted.
     * @returns any A successful response.
     * @returns runtimeError An unexpected error response.
     * @throws ApiError
     */
    public static experimentServiceDeleteExperiment(
        experimentId: string,
    ): CancelablePromise<Record<string, any> | runtimeError> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/apis/v2beta1/experiments/{experiment_id}',
            path: {
                'experiment_id': experimentId,
            },
        });
    }
    /**
     * Archives an experiment and the experiment's runs and recurring runs.
     * @param experimentId The ID of the experiment to be archived.
     * @returns any A successful response.
     * @returns runtimeError An unexpected error response.
     * @throws ApiError
     */
    public static experimentServiceArchiveExperiment(
        experimentId: string,
    ): CancelablePromise<Record<string, any> | runtimeError> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/apis/v2beta1/experiments/{experiment_id}:archive',
            path: {
                'experiment_id': experimentId,
            },
        });
    }
    /**
     * Restores an archived experiment. The experiment's archived runs and recurring
     * runs will stay archived.
     * @param experimentId The ID of the experiment to be restored.
     * @returns any A successful response.
     * @returns runtimeError An unexpected error response.
     * @throws ApiError
     */
    public static experimentServiceUnarchiveExperiment(
        experimentId: string,
    ): CancelablePromise<Record<string, any> | runtimeError> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/apis/v2beta1/experiments/{experiment_id}:unarchive',
            path: {
                'experiment_id': experimentId,
            },
        });
    }
}
