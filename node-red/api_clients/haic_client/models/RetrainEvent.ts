/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { RetrainingDetails } from './RetrainingDetails';
export type RetrainEvent = {
    retraining_time?: (string | null);
    initial_metrics?: (Record<string, number> | null);
    post_retraining_metrics?: (Record<string, number> | null);
    retraining_details?: (RetrainingDetails | null);
};

