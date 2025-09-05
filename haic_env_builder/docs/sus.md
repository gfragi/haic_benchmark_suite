# Public Survey Integration Guide

This document explains how developers can integrate and use the **Public Survey** form for collecting System Usability Scale (SUS), Ethics & Trust, and domain-specific responses from pilot users.

---

## 1. Accessing the Public Survey

The survey is available at the following route in the frontend:

```
/survey
```

Parameters are passed as **query strings**. Example:

```
https://hua-benchmarking.ddns.net//survey?pilot_tag=SmartEnergy&app_version=v3.2.0&ai_model_version=v1.0.0
```

### Required Parameters

- **`pilot_tag`** → Identifier of the pilot project (e.g., `SmartEnergy`).

### Optional Parameters

- **`app_version`** → Application version under evaluation.
- **`ai_model_version`** → AI model version used in the application.

If these parameters are provided, they will prefill the form and the fields will be **read-only**.

---

## 2. Prefilling Example

Example shareable link:

```
https://your-app-domain/survey?pilot_tag=Healthcare&app_version=2.0.1&ai_model_version=4.0.2
```

When opened:

- `Pilot tag` → `Healthcare` (read-only)
- `App version` → `2.0.1` (read-only)
- `AI model version` → `4.0.2` (read-only)

If no values are provided, the fields remain editable.

---

## 3. Survey Structure

The form includes:

- **Pilot metadata** (pilot tag, app version, AI model version)
- **System Usability Scale (SUS)**: 10 questions, each rated from 1 (Strongly disagree) to 5 (Strongly agree).
- **Ethics & Trust**: 5 questions, rated 1–5.
- **Domain-specific (optional)**: Custom items added by pilot teams.
- **Consent checkbox** (required to submit).

---

## 4. Data Submission

On submission, the form POSTs JSON data to the backend API:

**Endpoint:**
```
POST /api/v1/survey
```

**Payload Example:**

```json
{
  "survey_id": "uuid",
  "user_id": "anonymous",
  "timestamp": "2025-09-05T12:00:00.000Z",
  "pilot_tag": "SmartEnergy",
  "app_version": "v3.2.0",
  "ai_model_version": "v1.0.0",
  "tam_sus_responses": {
    "sus_q1": 5,
    "sus_q2": 2,
    "sus_q3": 4,
    ...
    "sus_q10": 3
  },
  "ethics_responses": {
    "q_fairness": 4,
    "q_transparency": 3,
    "q_privacy": 5,
    "q_accountability": 4,
    "q_trust": 5
  },
  "domain_specific": {
    "Perceived safety": 4,
    "Ease of integration": 5
  }
}
```

The backend validates and stores the survey results for later aggregation.

---

## 5. Sharing the Link

From the **Survey Dashboard**, coordinators can:

- Generate a survey link with `pilot_tag`, `app_version`, and `ai_model_version`.
- Copy the link or download a QR code.
- Share with pilot users for direct response collection.

**Template:**

```
{{origin}}/survey?pilot_tag=<YOUR_PILOT>&app_version=<VERSION>&ai_model_version=<MODEL>
```

Replace `<YOUR_PILOT>`, `<VERSION>`, and `<MODEL>` accordingly.

---

## 6. Notes for Developers

- Ensure CORS in backend allows frontend origin (e.g., `http://localhost:8080` in dev).
- In production, always generate absolute URLs with the domain.
- The form reads both **query** and **hash** parameters, so links will work even if Keycloak or another IdP appends `#state=...`.
- Missing required fields (e.g., `pilot_tag`) will block submission.

---

✅ With this setup, developers can integrate the survey into their applications, prefill metadata, and ensure consistent collection of user responses across pilots.
