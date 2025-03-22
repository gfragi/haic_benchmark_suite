/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AIModelData } from './AIModelData';
import type { InteractionData } from './InteractionData';
import type { PerformanceInfrastructure } from './PerformanceInfrastructure';
import type { PerformanceLogs } from './PerformanceLogs';
import type { RetrainEvent } from './RetrainEvent';
export type LogSchema = {
    session_id: string;
    user_id: string;
    ai_model_version?: (string | null);
    app_version: string;
    start_time: string;
    end_time: string;
    interaction_data?: (InteractionData | null);
    retrain_events?: (Array<RetrainEvent> | null);
    performance_infrastructure?: (PerformanceInfrastructure | null);
    performance_logs?: (PerformanceLogs | null);
    ai_model_data?: (AIModelData | null);
};

