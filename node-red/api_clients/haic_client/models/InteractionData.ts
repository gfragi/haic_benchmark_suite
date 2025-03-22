/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AlertData } from './AlertData';
import type { ReviewData } from './ReviewData';
import type { ValidationData } from './ValidationData';
export type InteractionData = {
    image_id?: (string | null);
    presentation_time?: (string | null);
    validation_data?: (ValidationData | null);
    review_data?: (ReviewData | null);
    application_id?: (string | null);
    justification_documents?: (string | null);
    submission_time?: (string | null);
    load_generation_data?: null;
    alert_data?: (AlertData | Array<AlertData> | null);
};

