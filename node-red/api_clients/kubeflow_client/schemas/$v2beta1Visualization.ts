/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $v2beta1Visualization = {
    properties: {
        type: {
            type: 'v2beta1VisualizationType',
        },
        source: {
            type: 'string',
            description: `Path pattern of input data to be used during generation of visualizations.
            This is required when creating the pipeline through CreateVisualization
            API.`,
        },
        arguments: {
            type: 'string',
            description: `Variables to be used during generation of a visualization.
            This should be provided as a JSON string.
            This is required when creating the pipeline through CreateVisualization
            API.`,
        },
        html: {
            type: 'string',
            description: `Output. Generated visualization html.`,
        },
        error: {
            type: 'string',
            description: `In case any error happens when generating visualizations, only
            visualization ID and the error message are returned. Client has the
            flexibility of choosing how to handle the error.`,
        },
    },
} as const;
