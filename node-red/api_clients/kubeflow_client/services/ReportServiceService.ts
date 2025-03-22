/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { runtimeError } from '../models/runtimeError';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class ReportServiceService {
    /**
     * @param requestBody ScheduledWorkflow a ScheduledWorkflow resource marshalled into a json string.
     * @returns any A successful response.
     * @returns runtimeError An unexpected error response.
     * @throws ApiError
     */
    public static reportServiceReportScheduledWorkflow(
        requestBody: string,
    ): CancelablePromise<Record<string, any> | runtimeError> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/apis/v2beta1/scheduledworkflows',
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * @param requestBody Workflow is a workflow custom resource marshalled into a json string.
     * @returns any A successful response.
     * @returns runtimeError An unexpected error response.
     * @throws ApiError
     */
    public static reportServiceReportWorkflow(
        requestBody: string,
    ): CancelablePromise<Record<string, any> | runtimeError> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/apis/v2beta1/workflows',
            body: requestBody,
            mediaType: 'application/json',
        });
    }
}
