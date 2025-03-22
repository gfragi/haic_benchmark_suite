/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { runtimeError } from '../models/runtimeError';
import type { v2beta1GetHealthzResponse } from '../models/v2beta1GetHealthzResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class HealthzServiceService {
    /**
     * Get healthz data.
     * @returns v2beta1GetHealthzResponse A successful response.
     * @returns runtimeError An unexpected error response.
     * @throws ApiError
     */
    public static healthzServiceGetHealthz(): CancelablePromise<v2beta1GetHealthzResponse | runtimeError> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/apis/v2beta1/healthz',
        });
    }
}
