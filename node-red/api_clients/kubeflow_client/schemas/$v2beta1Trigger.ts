/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $v2beta1Trigger = {
    description: `Trigger defines what starts a pipeline run.`,
    properties: {
        cron_schedule: {
            type: 'v2beta1CronSchedule',
        },
        periodic_schedule: {
            type: 'v2beta1PeriodicSchedule',
        },
    },
} as const;
