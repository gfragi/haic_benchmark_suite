/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { SystemMetrics } from './SystemMetrics';
export type ValidationData = {
    ai_detection_results?: (string | null);
    confidence_scores?: (Record<string, number> | null);
    validation_results?: (string | null);
    confidence_level?: (number | null);
    processing_time_seconds?: (number | null);
    validation_time?: (string | null);
    system_metrics?: (SystemMetrics | null);
};

