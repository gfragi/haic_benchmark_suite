/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $v2beta1RuntimeStatus = {
    description: `Timestamped representation of a runtime state with an optional error.`,
    properties: {
        update_time: {
            type: 'string',
            description: `Update time of this state.`,
            format: 'date-time',
        },
        state: {
            type: 'v2beta1RuntimeState',
        },
        error: {
            type: 'googlerpcStatus',
        },
    },
} as const;
