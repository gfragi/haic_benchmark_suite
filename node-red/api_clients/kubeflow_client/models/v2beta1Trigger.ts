/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { v2beta1CronSchedule } from './v2beta1CronSchedule';
import type { v2beta1PeriodicSchedule } from './v2beta1PeriodicSchedule';
/**
 * Trigger defines what starts a pipeline run.
 */
export type v2beta1Trigger = {
    cron_schedule?: v2beta1CronSchedule;
    periodic_schedule?: v2beta1PeriodicSchedule;
};

