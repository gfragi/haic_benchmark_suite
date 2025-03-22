/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class ReportingService {
    /**
     * Get Aggregated Results
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getAggregatedResultsReportingAggregateByDateGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/reporting/aggregate-by-date',
        });
    }
    /**
     * Get Time Series Data
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getTimeSeriesDataReportingTimeSeriesDataGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/reporting/time-series-data',
        });
    }
    /**
     * Generate Pdf Report
     * @returns any Successful Response
     * @throws ApiError
     */
    public static generatePdfReportReportingGenerateReportGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/reporting/generate-report',
        });
    }
}
