/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { v2beta1VisualizationType } from './v2beta1VisualizationType';
export type v2beta1Visualization = {
    type?: v2beta1VisualizationType;
    /**
     * Path pattern of input data to be used during generation of visualizations.
     * This is required when creating the pipeline through CreateVisualization
     * API.
     */
    source?: string;
    /**
     * Variables to be used during generation of a visualization.
     * This should be provided as a JSON string.
     * This is required when creating the pipeline through CreateVisualization
     * API.
     */
    arguments?: string;
    /**
     * Output. Generated visualization html.
     */
    html?: string;
    /**
     * In case any error happens when generating visualizations, only
     * visualization ID and the error message are returned. Client has the
     * flexibility of choosing how to handle the error.
     */
    error?: string;
};

