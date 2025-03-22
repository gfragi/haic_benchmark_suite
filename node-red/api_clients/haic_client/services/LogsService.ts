/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Body_upload_log_logs_upload_post } from '../models/Body_upload_log_logs_upload_post';
import type { LogSchema } from '../models/LogSchema';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class LogsService {
    /**
     * Upload Log
     * @param configurationId
     * @param formData
     * @returns any Successful Response
     * @throws ApiError
     */
    public static uploadLogLogsUploadPost(
        configurationId: number,
        formData: Body_upload_log_logs_upload_post,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/logs/upload',
            query: {
                'configuration_id': configurationId,
            },
            formData: formData,
            mediaType: 'multipart/form-data',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * List Logs
     * @param configId
     * @returns any Successful Response
     * @throws ApiError
     */
    public static listLogsLogsConfigIdGet(
        configId: number,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/logs/{config_id}',
            path: {
                'config_id': configId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Download Log
     * @param configId
     * @param logName
     * @returns any Successful Response
     * @throws ApiError
     */
    public static downloadLogLogsDownloadConfigIdLogNameGet(
        configId: number,
        logName: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/logs/download/{config_id}/{log_name}',
            path: {
                'config_id': configId,
                'log_name': logName,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Delete Log
     * @param configId
     * @param logName
     * @returns any Successful Response
     * @throws ApiError
     */
    public static deleteLogLogsConfigIdLogNameDelete(
        configId: number,
        logName: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/logs/{config_id}/{log_name}',
            path: {
                'config_id': configId,
                'log_name': logName,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Register Log
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public static registerLogLogsRegisterPost(
        requestBody: LogSchema,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/logs/register',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
