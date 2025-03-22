/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $runtimeError = {
    properties: {
        error: {
            type: 'string',
        },
        code: {
            type: 'number',
            format: 'int32',
        },
        message: {
            type: 'string',
        },
        details: {
            type: 'array',
            contains: {
                type: 'protobufAny',
            },
        },
    },
} as const;
