/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $v2beta1ArtifactList = {
    description: `A list of artifact metadata.`,
    properties: {
        artifact_ids: {
            type: 'array',
            contains: {
                type: 'string',
                format: 'int64',
            },
        },
    },
} as const;
