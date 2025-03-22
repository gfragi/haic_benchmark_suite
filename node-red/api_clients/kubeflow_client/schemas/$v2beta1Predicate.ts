/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $v2beta1Predicate = {
    description: `Predicate captures individual conditions that must be true for a resource
    being filtered.`,
    properties: {
        operation: {
            type: 'v2beta1PredicateOperation',
        },
        key: {
            type: 'string',
            description: `Key for the operation (first argument).`,
        },
        int_value: {
            type: 'number',
            description: `Integer.`,
            format: 'int32',
        },
        long_value: {
            type: 'string',
            description: `Long integer.`,
            format: 'int64',
        },
        string_value: {
            type: 'string',
            description: `String.`,
        },
        timestamp_value: {
            type: 'string',
            description: `Timestamp values will be converted to Unix time (seconds since the epoch)
            prior to being used in a filtering operation.`,
            format: 'date-time',
        },
        int_values: {
            type: 'PredicateIntValues',
        },
        long_values: {
            type: 'PredicateLongValues',
        },
        string_values: {
            type: 'PredicateStringValues',
        },
    },
} as const;
