/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { runtimeError } from '../models/runtimeError';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class AuthServiceService {
    /**
     * @param namespace
     * @param resources
     * @param verb
     * @returns any A successful response.
     * @returns runtimeError An unexpected error response.
     * @throws ApiError
     */
    public static authServiceAuthorize(
        namespace?: string,
        resources: 'UNASSIGNED_RESOURCES' | 'VIEWERS' = 'UNASSIGNED_RESOURCES',
        verb: 'UNASSIGNED_VERB' | 'CREATE' | 'GET' | 'DELETE' = 'UNASSIGNED_VERB',
    ): CancelablePromise<Record<string, any> | runtimeError> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/apis/v2beta1/auth',
            query: {
                'namespace': namespace,
                'resources': resources,
                'verb': verb,
            },
        });
    }
}
