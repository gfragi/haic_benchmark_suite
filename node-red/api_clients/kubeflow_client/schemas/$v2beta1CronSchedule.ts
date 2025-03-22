/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $v2beta1CronSchedule = {
    description: `CronSchedule allow scheduling the recurring run with unix-like cron.`,
    properties: {
        start_time: {
            type: 'string',
            description: `The start time of the cron job.`,
            format: 'date-time',
        },
        end_time: {
            type: 'string',
            description: `The end time of the cron job.`,
            format: 'date-time',
        },
        cron: {
            type: 'string',
        },
    },
} as const;
