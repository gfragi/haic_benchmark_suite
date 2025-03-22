/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class LogGeneratorService {
    /**
     * Generate Log Endpoint
     * @param appType Type of application to generate logs for
     * @param count Number of log entries to generate
     * @param startDate Start date of the log period
     * @param endDate End date of the log period
     * @param aiModelVersionRange Range of model versions
     * @returns any Successful Response
     * @throws ApiError
     */
    public static generateLogEndpointLogGeneratorGenerateGet(
        appType: string = 'radiologist',
        count: number = 100,
        startDate: string = '2024-02-10T13:00:00Z',
        endDate: string = '2024-05-10T13:00:00Z',
        aiModelVersionRange: string = '1.0.0 - 3.0.0',
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/log-generator/generate',
            query: {
                'app_type': appType,
                'count': count,
                'start_date': startDate,
                'end_date': endDate,
                'ai_model_version_range': aiModelVersionRange,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Download Log
     * @param filePath
     * @returns any Successful Response
     * @throws ApiError
     */
    public static downloadLogLogGeneratorDownloadGet(
        filePath: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/log-generator/download/',
            query: {
                'file_path': filePath,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
