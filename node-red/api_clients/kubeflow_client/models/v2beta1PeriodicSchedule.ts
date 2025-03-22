/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * PeriodicSchedule allow scheduling the recurring run periodically with certain interval.
 */
export type v2beta1PeriodicSchedule = {
    /**
     * The start time of the periodic recurring run.
     */
    start_time?: string;
    /**
     * The end time of the periodic recurring run.
     */
    end_time?: string;
    /**
     * The time interval between the starting time of consecutive recurring runs.
     */
    interval_second?: string;
};

