/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $v2beta1ReadArtifactResponse = {
    properties: {
        data: {
            type: 'string',
            description: `Byte array of the artifact content.`,
            format: 'byte',
            pattern: '^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$',
        },
    },
} as const;
