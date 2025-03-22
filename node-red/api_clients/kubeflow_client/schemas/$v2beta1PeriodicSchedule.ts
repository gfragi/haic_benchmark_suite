/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $v2beta1PeriodicSchedule = {
    description: `PeriodicSchedule allow scheduling the recurring run periodically with certain interval.`,
    properties: {
        start_time: {
            type: 'string',
            description: `The start time of the periodic recurring run.`,
            format: 'date-time',
        },
        end_time: {
            type: 'string',
            description: `The end time of the periodic recurring run.`,
            format: 'date-time',
        },
        interval_second: {
            type: 'string',
            description: `The time interval between the starting time of consecutive recurring runs.`,
            format: 'int64',
        },
    },
} as const;
