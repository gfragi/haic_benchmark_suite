/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { runtimeError } from '../models/runtimeError';
import type { v2beta1Visualization } from '../models/v2beta1Visualization';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class VisualizationServiceService {
    /**
     * @param namespace
     * @param requestBody
     * @returns v2beta1Visualization A successful response.
     * @returns runtimeError An unexpected error response.
     * @throws ApiError
     */
    public static visualizationServiceCreateVisualizationV1(
        namespace: string,
        requestBody: v2beta1Visualization,
    ): CancelablePromise<v2beta1Visualization | runtimeError> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/apis/v2beta1/visualizations/{namespace}',
            path: {
                'namespace': namespace,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
}
