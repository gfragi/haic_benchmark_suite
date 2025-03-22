/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Operation is the operation to apply.
 *
 * - OPERATION_UNSPECIFIED: Default operation. This operation is not used.
 * - EQUALS: Operation on scalar values. Only applies to one of |int_value|,
 * |long_value|, |string_value| or |timestamp_value|.
 * - NOT_EQUALS: Negated EQUALS.
 * - GREATER_THAN: Greater than operation.
 * - GREATER_THAN_EQUALS: Greater than or equals operation.
 * - LESS_THAN: Less than operation.
 * - LESS_THAN_EQUALS: Less than or equals operation
 * - IN: Checks if the value is a member of a given array, which should be one of
 * |int_values|, |long_values| or |string_values|.
 * - IS_SUBSTRING: Checks if the value contains |string_value| as a substring match. Only
 * applies to |string_value|.
 */
export enum v2beta1PredicateOperation {
    OPERATION_UNSPECIFIED = 'OPERATION_UNSPECIFIED',
    EQUALS = 'EQUALS',
    NOT_EQUALS = 'NOT_EQUALS',
    GREATER_THAN = 'GREATER_THAN',
    GREATER_THAN_EQUALS = 'GREATER_THAN_EQUALS',
    LESS_THAN = 'LESS_THAN',
    LESS_THAN_EQUALS = 'LESS_THAN_EQUALS',
    IN = 'IN',
    IS_SUBSTRING = 'IS_SUBSTRING',
}
