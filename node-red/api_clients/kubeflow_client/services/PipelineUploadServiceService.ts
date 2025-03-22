/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { googlerpcStatus } from '../models/googlerpcStatus';
import type { v2beta1Pipeline } from '../models/v2beta1Pipeline';
import type { v2beta1PipelineVersion } from '../models/v2beta1PipelineVersion';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class PipelineUploadServiceService {
    /**
     * @param formData
     * @param name
     * @param description
     * @param namespace
     * @returns v2beta1Pipeline
     * @returns googlerpcStatus
     * @throws ApiError
     */
    public static uploadPipeline(
        formData: {
            /**
             * The pipeline to upload. Maximum size of 32MB is supported.
             */
            uploadfile: Blob;
        },
        name?: string,
        description?: string,
        namespace?: string,
    ): CancelablePromise<v2beta1Pipeline | googlerpcStatus> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/apis/v2beta1/pipelines/upload',
            query: {
                'name': name,
                'description': description,
                'namespace': namespace,
            },
            formData: formData,
            mediaType: 'multipart/form-data',
        });
    }
    /**
     * @param formData
     * @param name
     * @param pipelineid
     * @param description
     * @returns v2beta1PipelineVersion
     * @returns googlerpcStatus
     * @throws ApiError
     */
    public static uploadPipelineVersion(
        formData: {
            /**
             * The pipeline to upload. Maximum size of 32MB is supported.
             */
            uploadfile: Blob;
        },
        name?: string,
        pipelineid?: string,
        description?: string,
    ): CancelablePromise<v2beta1PipelineVersion | googlerpcStatus> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/apis/v2beta1/pipelines/upload_version',
            query: {
                'name': name,
                'pipelineid': pipelineid,
                'description': description,
            },
            formData: formData,
            mediaType: 'multipart/form-data',
        });
    }
}
