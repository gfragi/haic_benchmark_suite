<template>
  <v-container class="py-6" style="max-width: 900px">
    <v-card class="pa-6" elevation="2">
      <v-card-title class="text-h5 font-weight-bold"
        >Public Survey</v-card-title
      >
      <v-card-subtitle class="mb-4">
        Help us evaluate the platform. This form is anonymous and takes ~3
        minutes.
      </v-card-subtitle>

      <v-alert v-if="!pilotTag" type="warning" variant="tonal" class="mb-4">
        Missing <code>pilot_tag</code> in the URL. You can type it manually
        below, or open the link with <code>?pilot_tag=YourPilot</code>.
      </v-alert>

      <v-form ref="formRef" v-model="formValid" @submit.prevent="onSubmit">
        <!-- Context -->
        <v-row>
          <v-col cols="12" md="6">
            <v-text-field
              label="Pilot tag"
              v-model="pilotTag"
              :readonly="pilotTagFromUrl"
              prepend-inner-icon="mdi-tag-outline"
              hide-details
            />
          </v-col>
          <v-col cols="12" md="6">
            <v-text-field
              label="App version (optional)"
              v-model="appVersion"
              prepend-inner-icon="mdi-application-cog"
              hide-details
            />
          </v-col>
          <v-col cols="12" md="6">
            <v-text-field
              label="AI model version (optional)"
              v-model="aiModelVersion"
              prepend-inner-icon="mdi-robot-outline"
              hide-details
            />
          </v-col>
        </v-row>

        <v-divider class="my-6" />

        <!-- SUS (10 items) -->
        <div class="text-h6 mb-2">System Usability Scale (SUS)</div>
        <div class="text-body-2 mb-4">
          Please rate each statement from 1 (Strongly disagree) to 5 (Strongly
          agree).
        </div>

        <div v-for="(q, idx) in susQuestions" :key="q.key" class="mb-3">
          <div class="mb-1">
            <strong>{{ idx + 1 }}.</strong> {{ q.label }}
          </div>
          <div class="d-flex align-center gap-2">
            <span class="text-caption mr-2">1</span>
            <v-btn-toggle
              class="my-2"
              divided
              density="comfortable"
              :model-value="sus[q.key]"
              @update:modelValue="(v) => (sus[q.key] = v)"
            >
              <v-btn v-for="n in [1, 2, 3, 4, 5]" :key="n" :value="n">{{
                n
              }}</v-btn>
            </v-btn-toggle>
            <span class="text-caption ml-2">5</span>
          </div>
          <v-divider class="mt-3" />
        </div>

        <v-divider class="my-6" />

        <!-- Ethics (5 items) -->
        <div class="text-h6 mb-2">Ethics & Trust</div>
        <div class="text-body-2 mb-4">
          Rate from 1 (Strongly disagree) to 5 (Strongly agree).
        </div>

        <div v-for="(q, idx) in ethicsQuestions" :key="q.key" class="mb-3">
          <div class="mb-1">
            <strong>{{ idx + 1 }}.</strong> {{ q.label }}
          </div>
          <div class="d-flex align-center gap-2">
            <span class="text-caption mr-2">1</span>
            <v-btn-toggle
              class="my-2"
              divided
              density="comfortable"
              :model-value="ethics[q.key]"
              @update:modelValue="(v) => (ethics[q.key] = v)"
            >
              <v-btn v-for="n in [1, 2, 3, 4, 5]" :key="n" :value="n">{{
                n
              }}</v-btn>
            </v-btn-toggle>
            <span class="text-caption ml-2">5</span>
          </div>
          <v-divider class="mt-3" />
        </div>

        <v-divider class="my-6" />

        <!-- Domain-specific (optional, dynamic) -->
        <!-- Domain-specific (optional) -->
        <div class="d-flex align-center mb-2">
          <div class="text-h6">
            Domain-specific
            <span v-if="domainSchema?.name" class="text-caption"
              >· {{ domainSchema.name }}</span
            >
          </div>
          <v-spacer />
          <v-chip v-if="schemaId" size="small" class="ml-2" label
            >schema_id={{ schemaId }}</v-chip
          >
        </div>

        <v-alert
          v-if="domainError"
          type="warning"
          variant="tonal"
          class="mb-3"
          >{{ domainError }}</v-alert
        >

        <!-- A) Schema-driven rendering -->
        <div v-if="domainSchema && domainSchema.questions?.length">
          <div
            v-for="(q, i) in domainSchema.questions"
            :key="q.id"
            class="mb-4"
          >
            <div class="mb-2">
              <strong>{{ i + 1 }}.</strong>
              <span>{{ q.label }}</span>
              <span v-if="q.required" class="text-error ml-1">*</span>
              <div v-if="q.group" class="text-caption text-medium-emphasis">
                {{ q.group }}
              </div>
            </div>

            <!-- Likert -->
            <div v-if="q.type === 'likert'">
              <div class="d-flex align-center gap-2">
                <span class="text-caption">{{
                  q.scale?.min_label || "1"
                }}</span>
                <v-btn-toggle
                  v-model="domainAnswers[q.id]"
                  divided
                  mandatory
                  class="mx-2"
                >
                  <v-btn v-for="n in q.scale?.max || 5" :key="n" :value="n">{{
                    n
                  }}</v-btn>
                </v-btn-toggle>
                <span class="text-caption">{{
                  q.scale?.max_label || "5"
                }}</span>
              </div>
            </div>

            <!-- Single choice -->
            <v-select
              v-else-if="q.type === 'single'"
              v-model="domainAnswers[q.id]"
              :items="q.options || []"
              label="Select"
              :rules="q.required ? [(v) => !!v || 'Required'] : []"
              hide-details="auto"
            />

            <!-- Multi choice -->
            <v-select
              v-else-if="q.type === 'multi'"
              v-model="domainAnswers[q.id]"
              :items="q.options || []"
              label="Select one or more"
              multiple
              chips
              :rules="
                q.required ? [(v) => !!(v && v.length) || 'Required'] : []
              "
              hide-details="auto"
            />

            <!-- Number -->
            <v-text-field
              v-else-if="q.type === 'number'"
              v-model.number="domainAnswers[q.id]"
              type="number"
              hide-details="auto"
              :rules="q.required ? [(v) => v !== null || 'Required'] : []"
            />

            <!-- Boolean -->
            <v-switch
              v-else-if="q.type === 'boolean'"
              v-model="domainAnswers[q.id]"
              color="primary"
              hide-details
              inset
            />

            <!-- Text (default) -->
            <v-text-field
              v-else
              v-model="domainAnswers[q.id]"
              label="Your answer"
              :rules="q.required ? [(v) => !!v || 'Required'] : []"
              hide-details="auto"
            />

            <v-divider class="mt-3" />
          </div>
        </div>

        <!-- B) Fallback to your ad-hoc builder when no schema exists -->
        <div v-else>
          <div class="d-flex align-center mb-2">
            <div class="text-body-2">
              No predefined questions for this link.
            </div>
            <v-spacer />
            <v-btn
              size="small"
              variant="text"
              prepend-icon="mdi-plus"
              @click="addDomainItem"
              >Add item</v-btn
            >
          </div>
          <div
            v-if="
              (!domainSchema || !domainSchema.questions?.length) &&
              domainItems.length === 0
            "
            class="text-body-2 mb-2"
          >
            You can add custom items relevant to your pilot.
          </div>
        </div>

        <v-divider class="my-6" />

        <v-row v-for="(item, i) in domainItems" :key="item.id" class="mb-2">
          <v-col cols="12" md="7">
            <v-text-field
              :label="`Item ${i + 1} label`"
              v-model="item.label"
              placeholder="e.g., Perceived safety of suggestions"
            />
          </v-col>
          <v-col cols="10" md="4">
            <v-btn-toggle
              class="my-2"
              divided
              density="comfortable"
              :model-value="item.value"
              @update:modelValue="(v) => (item.value = v)"
            >
              <v-btn v-for="n in [1, 2, 3, 4, 5]" :key="n" :value="n">{{
                n
              }}</v-btn>
            </v-btn-toggle>
          </v-col>
          <v-col cols="2" md="1" class="d-flex align-center">
            <v-btn
              icon="mdi-delete"
              variant="text"
              @click="removeDomainItem(i)"
            />
          </v-col>
        </v-row>

        <v-divider class="my-6" />

        <v-checkbox
          v-model="consent"
          :rules="[(v) => !!v || 'Required']"
          label="I consent to my anonymized responses being stored for research & QA purposes."
        />

        <v-alert v-if="submitError" type="error" variant="tonal" class="mt-4">{{
          submitError
        }}</v-alert>
        <v-alert v-if="submitOk" type="success" variant="tonal" class="mt-4">
          Thank you! Your response has been recorded. You may close this tab.
        </v-alert>

        <div class="d-flex gap-2 mt-6">
          <v-btn
            :loading="submitting"
            color="primary"
            type="submit"
            :disabled="!pilotTag"
            >Submit</v-btn
          >
          <v-btn variant="text" @click="resetForm">Reset</v-btn>
        </div>
      </v-form>
    </v-card>
  </v-container>
</template>

<script setup>
const userId = ref(getParam("user_id") || "anonymous");

const formRef = ref(null);
const formValid = ref(false);
const consent = ref(false);
const submitting = ref(false);
const submitOk = ref(false);
const submitError = ref("");

import { ref, computed, onMounted, watch } from "vue";
const pilotTagFromUrl = !!getParam("pilot_tag");
const pilotTag = ref(
  getParam("pilot_tag") || sessionStorage.getItem("pilot_tag") || ""
);
const appVersion = ref(
  getParam("app_version") || sessionStorage.getItem("app_version") || ""
);
const aiModelVersion = ref(
  getParam("ai_model_version") ||
    sessionStorage.getItem("ai_model_version") ||
    ""
);

import {
  fetchSchemaById,
  fetchLatestSchemaForPilot,
} from "@/services/surveySchemas";

const schemaId = ref(getParam("schema_id") || "");
const domainSchema = ref(null); // { schema_id, questions: [...] }
const domainAnswers = ref({}); // keyed by question.id when schema-driven
const domainError = ref("");

onMounted(async () => {
  try {
    if (schemaId.value) {
      domainSchema.value = await fetchSchemaById(schemaId.value);
    } else if (pilotTag.value) {
      const latest = await fetchLatestSchemaForPilot(pilotTag.value);
      if (latest) domainSchema.value = latest; // optional auto-load
    }

    // initialize answer model for required questions
    if (domainSchema.value?.questions?.length) {
      for (const q of domainSchema.value.questions) {
        if (q.type === "multi") domainAnswers.value[q.id] = [];
        else if (q.type === "boolean") domainAnswers.value[q.id] = false;
        else domainAnswers.value[q.id] = null;
      }
    }
  } catch (e) {
    domainError.value = e?.message || "Failed to load extra questions.";
  }
});

// persist context fields during the session
watch([pilotTag, appVersion, aiModelVersion], ([p, a, m]) => {
  sessionStorage.setItem("pilot_tag", p || "");
  sessionStorage.setItem("app_version", a || "");
  sessionStorage.setItem("ai_model_version", m || "");
});

const sus = ref({
  sus_q1: 0,
  sus_q2: 0,
  sus_q3: 0,
  sus_q4: 0,
  sus_q5: 0,
  sus_q6: 0,
  sus_q7: 0,
  sus_q8: 0,
  sus_q9: 0,
  sus_q10: 0,
});

const ethics = ref({
  q_fairness: 0,
  q_transparency: 0,
  q_privacy: 0,
  q_accountability: 0,
  q_trust: 0,
});

const domainItems = ref([]);
function addDomainItem() {
  domainItems.value.push({
    id: crypto.randomUUID?.() || Math.random().toString(36).slice(2),
    label: "",
    value: 0,
  });
}
function removeDomainItem(i) {
  domainItems.value.splice(i, 1);
}

const susQuestions = [
  {
    key: "sus_q1",
    label: "I think that I would like to use this system frequently.",
  },
  { key: "sus_q2", label: "I found the system unnecessarily complex." },
  { key: "sus_q3", label: "I thought the system was easy to use." },
  {
    key: "sus_q4",
    label:
      "I think that I would need the support of a technical person to be able to use this system.",
  },
  {
    key: "sus_q5",
    label: "I found the various functions in this system were well integrated.",
  },
  {
    key: "sus_q6",
    label: "I thought there was too much inconsistency in this system.",
  },
  {
    key: "sus_q7",
    label:
      "I would imagine that most people would learn to use this system very quickly.",
  },
  { key: "sus_q8", label: "I found the system very cumbersome to use." },
  { key: "sus_q9", label: "I felt very confident using the system." },
  {
    key: "sus_q10",
    label:
      "I needed to learn a lot of things before I could get going with this system.",
  },
];

const ethicsQuestions = [
  {
    key: "q_fairness",
    label: "The system treats users fairly and without bias.",
  },
  { key: "q_transparency", label: "The system explains its outputs clearly." },
  { key: "q_privacy", label: "The system respects user privacy." },
  {
    key: "q_accountability",
    label: "It is clear who is responsible for the system’s behavior.",
  },
  { key: "q_trust", label: "I trust the system’s recommendations." },
];

const allAnswered = computed(() => {
  const susOk = Object.values(sus.value).every((v) => v >= 1 && v <= 5);
  const ethOk = Object.values(ethics.value).every((v) => v >= 1 && v <= 5);
  return susOk && ethOk;
});

// SUS scoring (Brooke 1996): odd items (1,3,5,7,9): x-1; even items (2,4,6,8,10): 5-x; sum*2.5
const susScore = computed(() => {
  const v = sus.value;
  const odd =
    v.sus_q1 -
    1 +
    (v.sus_q3 - 1) +
    (v.sus_q5 - 1) +
    (v.sus_q7 - 1) +
    (v.sus_q9 - 1);
  const even =
    5 -
    v.sus_q2 +
    (5 - v.sus_q4) +
    (5 - v.sus_q6) +
    (5 - v.sus_q8) +
    (5 - v.sus_q10);
  const raw = odd + even;
  const score = raw * 2.5;
  return Number.isFinite(score) ? Math.max(0, Math.min(100, score)) : 0;
});

const ethicsAvg = computed(() => {
  const vals = Object.values(ethics.value).filter((x) => x >= 1);
  if (!vals.length) return 0;
  return +(vals.reduce((a, b) => a + b, 0) / vals.length).toFixed(2);
});
// function sanitizeEndpoint(url) {
//   const envUrl = (url || "").replace(/\/+$/, "");
//   if (!/^https?:\/\//i.test(envUrl)) return envUrl; // allow relative for dev
//   try {
//     const u = new URL(envUrl);
//     return u.toString().replace(/\/+$/, "");
//   } catch {
//     return envUrl;
//   }
// }

function buildPayload() {
  // A) schema-driven case
  if (domainSchema.value?.questions?.length) {
    // Validate required
    for (const q of domainSchema.value.questions) {
      if (q.required) {
        const v = domainAnswers.value[q.id];
        const ok =
          (q.type === "multi" && Array.isArray(v) && v.length > 0) ||
          (q.type !== "multi" && v !== null && v !== undefined && v !== "");
        if (!ok) throw new Error(`Please answer: ${q.label}`);
      }
    }
    return {
      user_id: userId.value || "anonymous",
      pilot_tag: pilotTag.value,
      app_version: appVersion.value || "unknown",
      ai_model_version: aiModelVersion.value || "unknown",
      schema_id: domainSchema.value.schema_id, // NEW
      tam_sus_responses: { ...sus.value },
      ethics_responses: { ...ethics.value },
      domain_specific: { ...domainAnswers.value }, // keyed by q.id
      _client_summaries: {
        sus_score: susScore.value,
        ethics_avg: ethicsAvg.value,
      },
    };
  }

  // B) ad-hoc fallback (your current behavior)
  const domain_specific = {};
  for (const item of domainItems.value) {
    if (!item.label) continue;
    domain_specific[item.id || item.label] = Number(item.value) || 0;
  }
  return {
    user_id: userId.value || "anonymous",
    pilot_tag: pilotTag.value,
    app_version: appVersion.value || "unknown",
    ai_model_version: aiModelVersion.value || "unknown",
    tam_sus_responses: { ...sus.value },
    ethics_responses: { ...ethics.value },
    domain_specific,
    _client_summaries: {
      sus_score: susScore.value,
      ethics_avg: ethicsAvg.value,
    },
  };
}
function getApiBase() {
  const SURVEY_EP =
    import.meta?.env?.VITE_SURVEY_ENDPOINT ||
    process?.env?.VUE_APP_SURVEY_ENDPOINT ||
    "";

  // If SURVEY_ENDPOINT is absolute, infer its origin
  let inferred = "";
  try {
    if (SURVEY_EP && /^https?:\/\//i.test(SURVEY_EP)) {
      const u = new URL(SURVEY_EP);
      inferred = `${u.protocol}//${u.host}`;
    }
  } catch {
    inferred = "";
  }

  // Dev guess: UI on :8080 -> API on :8000
  const devGuess =
    typeof window !== "undefined" &&
    (window.location.hostname === "localhost" ||
      window.location.hostname === "127.0.0.1") &&
    window.location.port === "8080"
      ? `${window.location.protocol}//${window.location.hostname}:8000`
      : "";

  const explicit =
    import.meta?.env?.VITE_API_BASE || process?.env?.VUE_APP_API_BASE || "";

  return (explicit || inferred || devGuess || "").replace(/\/+$/, "");
}

const SURVEY_POST_URL = `${getApiBase()}/api/v1/survey`.replace(/\/+$/, "");

async function onSubmit() {
  submitError.value = "";
  submitOk.value = false;

  const { valid } = await formRef.value.validate();
  if (!valid) return;
  if (!allAnswered.value) {
    submitError.value = "Please answer all SUS and Ethics questions.";
    return;
  }
  if (!pilotTag.value) {
    submitError.value = "Missing pilot_tag.";
    return;
  }
  if (!consent.value) {
    submitError.value = "Please provide consent to proceed.";
    return;
  }

  submitting.value = true;
  try {
    const res = await fetch(SURVEY_POST_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(buildPayload()),
    });

    const bodyText = await res.text().catch(() => "");
    if (!res.ok) {
      const detail = bodyText?.slice(0, 300) || res.statusText;
      throw new Error(`POST ${res.status} — ${detail}`);
    }

    submitOk.value = true;
    resetForm();
  } catch (e) {
    submitError.value = e?.message || "Submission failed.";
  } finally {
    submitting.value = false;
  }
}

function getParam(name) {
  const qs = new URLSearchParams(window.location.search);
  if (qs.has(name)) return qs.get(name);
  const hash = window.location.hash.startsWith("#")
    ? window.location.hash.slice(1)
    : window.location.hash;
  const hs = new URLSearchParams(hash);
  return hs.get(name);
}

function resetForm() {
  consent.value = false;
  for (const k of Object.keys(sus.value)) sus.value[k] = 0;
  for (const k of Object.keys(ethics.value)) ethics.value[k] = 0;
  domainItems.value = [];
}
</script>

<style scoped>
.gap-2 {
  gap: 0.5rem;
}
</style>
