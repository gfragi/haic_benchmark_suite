/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { v2beta1Experiment } from './v2beta1Experiment';
export type v2beta1ListExperimentsResponse = {
    /**
     * A list of experiments returned.
     */
    experiments?: Array<v2beta1Experiment>;
    /**
     * The number of experiments for the given query.
     */
    total_size?: number;
    /**
     * The token to list the next page of experiments.
     */
    next_page_token?: string;
};

