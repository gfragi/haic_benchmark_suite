/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PredicateIntValues } from './PredicateIntValues';
import type { PredicateLongValues } from './PredicateLongValues';
import type { PredicateStringValues } from './PredicateStringValues';
import type { v2beta1PredicateOperation } from './v2beta1PredicateOperation';
/**
 * Predicate captures individual conditions that must be true for a resource
 * being filtered.
 */
export type v2beta1Predicate = {
    operation?: v2beta1PredicateOperation;
    /**
     * Key for the operation (first argument).
     */
    key?: string;
    /**
     * Integer.
     */
    int_value?: number;
    /**
     * Long integer.
     */
    long_value?: string;
    /**
     * String.
     */
    string_value?: string;
    /**
     * Timestamp values will be converted to Unix time (seconds since the epoch)
     * prior to being used in a filtering operation.
     */
    timestamp_value?: string;
    int_values?: PredicateIntValues;
    long_values?: PredicateLongValues;
    string_values?: PredicateStringValues;
};

