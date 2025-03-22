/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $InteractionData = {
    properties: {
        image_id: {
            type: 'any-of',
            contains: [{
                type: 'string',
            }, {
                type: 'null',
            }],
        },
        presentation_time: {
            type: 'any-of',
            contains: [{
                type: 'string',
            }, {
                type: 'null',
            }],
        },
        validation_data: {
            type: 'any-of',
            contains: [{
                type: 'ValidationData',
            }, {
                type: 'null',
            }],
        },
        review_data: {
            type: 'any-of',
            contains: [{
                type: 'ReviewData',
            }, {
                type: 'null',
            }],
        },
        application_id: {
            type: 'any-of',
            contains: [{
                type: 'string',
            }, {
                type: 'null',
            }],
        },
        justification_documents: {
            type: 'any-of',
            contains: [{
                type: 'string',
            }, {
                type: 'null',
            }],
        },
        submission_time: {
            type: 'any-of',
            contains: [{
                type: 'string',
            }, {
                type: 'null',
            }],
        },
        load_generation_data: {
            type: 'any-of',
            contains: [{
                type: 'null',
            }],
        },
        alert_data: {
            type: 'any-of',
            contains: [{
                type: 'AlertData',
            }, {
                type: 'array',
                contains: {
                    type: 'AlertData',
                },
            }, {
                type: 'null',
            }],
        },
    },
} as const;
