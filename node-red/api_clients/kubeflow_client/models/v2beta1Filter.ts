/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { v2beta1Predicate } from './v2beta1Predicate';
/**
 * Filter is used to filter resources returned from a ListXXX request.
 *
 * Example filters:
 * 1) Filter runs with status = 'Running'
 * filter {
     * predicate {
         * key: "status"
         * operation: EQUALS
         * string_value: "Running"
         * }
         * }
         *
         * 2) Filter runs that succeeded since Dec 1, 2018
         * filter {
             * predicate {
                 * key: "status"
                 * operation: EQUALS
                 * string_value: "Succeeded"
                 * }
                 * predicate {
                     * key: "created_at"
                     * operation: GREATER_THAN
                     * timestamp_value {
                         * seconds: 1543651200
                         * }
                         * }
                         * }
                         *
                         * 3) Filter runs with one of labels 'label_1' or 'label_2'
                         *
                         * filter {
                             * predicate {
                                 * key: "label"
                                 * operation: IN
                                 * string_values {
                                     * value: 'label_1'
                                     * value: 'label_2'
                                     * }
                                     * }
                                     * }
                                     */
                                    export type v2beta1Filter = {
                                        /**
                                         * All predicates are AND-ed when this filter is applied.
                                         */
                                        predicates?: Array<v2beta1Predicate>;
                                    };

