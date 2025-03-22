/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * CronSchedule allow scheduling the recurring run with unix-like cron.
 */
export type v2beta1CronSchedule = {
    /**
     * The start time of the cron job.
     */
    start_time?: string;
    /**
     * The end time of the cron job.
     */
    end_time?: string;
    cron?: string;
};

