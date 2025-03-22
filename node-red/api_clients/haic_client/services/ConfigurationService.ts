/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EvaluationConfigSchema } from '../models/EvaluationConfigSchema';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class ConfigurationService {
    /**
     * Create Configuration
     * @param requestBody
     * @returns EvaluationConfigSchema Successful Response
     * @throws ApiError
     */
    public static createConfigurationConfigurationNewPost(
        requestBody: EvaluationConfigSchema,
    ): CancelablePromise<EvaluationConfigSchema> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/configuration/new',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Configuration
     * @param configurationId
     * @returns EvaluationConfigSchema Successful Response
     * @throws ApiError
     */
    public static getConfigurationConfigurationConfigurationIdGet(
        configurationId: number,
    ): CancelablePromise<EvaluationConfigSchema> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/configuration/{configuration_id}',
            path: {
                'configuration_id': configurationId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get All Configurations
     * @returns EvaluationConfigSchema Successful Response
     * @throws ApiError
     */
    public static getAllConfigurationsConfigurationListGet(): CancelablePromise<Array<EvaluationConfigSchema>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/configuration/list/',
        });
    }
    /**
     * Update Configuration
     * @param configurationId
     * @param requestBody
     * @returns EvaluationConfigSchema Successful Response
     * @throws ApiError
     */
    public static updateConfigurationConfigurationUpdateConfigurationIdPut(
        configurationId: number,
        requestBody: EvaluationConfigSchema,
    ): CancelablePromise<EvaluationConfigSchema> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/configuration/update/{configuration_id}',
            path: {
                'configuration_id': configurationId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Delete Configuration
     * @param configurationId
     * @returns any Successful Response
     * @throws ApiError
     */
    public static deleteConfigurationConfigurationDeleteConfigurationIdDelete(
        configurationId: number,
    ): CancelablePromise<Record<string, any>> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/configuration/delete/{configuration_id}',
            path: {
                'configuration_id': configurationId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
