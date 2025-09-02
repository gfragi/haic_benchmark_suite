<template>
  <BaseLayout>
    <v-container class="py-6" style="max-width: 900px">
      <v-card class="pa-6" elevation="2">
        <v-card-title class="text-h5 font-weight-bold">
          Public Survey
        </v-card-title>
        <v-card-subtitle class="mb-4">
          Help us evaluate the platform. This form is anonymous and takes ~3
          minutes.
        </v-card-subtitle>

        <v-alert v-if="!pilotTag" type="warning" variant="tonal" class="mb-4">
          Missing <code>pilot_tag</code> in the URL. Responses will not be
          accepted until it's provided.
        </v-alert>

        <v-form ref="formRef" v-model="formValid" @submit.prevent="onSubmit">
          <!-- Context -->
          <v-row>
            <v-col cols="12" md="6">
              <v-text-field
                label="Pilot tag"
                v-model="pilotTag"
                :readonly="true"
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

          <QuestionRow
            v-for="(q, idx) in susQuestions"
            :key="q.key"
            :index="idx + 1"
            :label="q.label"
            v-model="sus[q.key]"
          />

          <v-divider class="my-6" />

          <!-- Ethics (5 items) -->
          <div class="text-h6 mb-2">Ethics & Trust</div>
          <div class="text-body-2 mb-4">
            Rate from 1 (Strongly disagree) to 5 (Strongly agree).
          </div>

          <QuestionRow
            v-for="(q, idx) in ethicsQuestions"
            :key="q.key"
            :index="idx + 1"
            :label="q.label"
            v-model="ethics[q.key]"
          />

          <v-divider class="my-6" />

          <!-- Domain-specific (optional, dynamic) -->
          <div class="d-flex align-center mb-2">
            <div class="text-h6">Domain-specific (optional)</div>
            <v-spacer />
            <v-btn
              size="small"
              variant="text"
              prepend-icon="mdi-plus"
              @click="addDomainItem"
              >Add item</v-btn
            >
          </div>
          <div v-if="domainItems.length === 0" class="text-body-2 mb-2">
            You can add custom items relevant to your pilot.
          </div>

          <v-row v-for="(item, i) in domainItems" :key="item.id" class="mb-2">
            <v-col cols="12" md="7">
              <v-text-field
                :label="`Item ${i + 1} label`"
                v-model="item.label"
                placeholder="e.g., Perceived safety of suggestions"
              />
            </v-col>
            <v-col cols="10" md="4">
              <Likert v-model="item.value" />
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

          <v-alert
            v-if="submitError"
            type="error"
            variant="tonal"
            class="mt-4"
            >{{ submitError }}</v-alert
          >
          <v-alert v-if="submitOk" type="success" variant="tonal" class="mt-4"
            >Thank you! Your response has been recorded. You may close this
            tab.</v-alert
          >

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

      <!-- Share link helper (visible to coordinators if no pilot_tag provided) -->
      <v-card v-if="!pilotTag" class="pa-4 mt-6" variant="tonal">
        <div class="text-subtitle-1 font-weight-medium mb-2">
          Shareable link template
        </div>
        <code class="text-body-2"
          >{{
            origin
          }}/survey/?pilot_tag=<em>&lt;YOUR_PILOT_TAG&gt;</em>&amp;app_version=<em>v1</em>&amp;ai_model_version=<em
            >gpt-4o</em
          ></code
        >
      </v-card>
    </v-container>
  </BaseLayout>
</template>

<script setup>
import { ref, computed } from "vue";

// --- Helpers ---
const origin = window?.location?.origin || "";
const url = new URL(window.location.href);

const pilotTag = ref(url.searchParams.get("pilot_tag") || "");
const appVersion = ref(url.searchParams.get("app_version") || "");
const aiModelVersion = ref(url.searchParams.get("ai_model_version") || "");

const formRef = ref(null);
const formValid = ref(false);
const consent = ref(false);
const submitting = ref(false);
const submitOk = ref(false);
const submitError = ref("");

// Likert (1..5)
// const makeEmpty = () => 0;

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
  domainItems.value.push({ id: crypto.randomUUID(), label: "", value: 0 });
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

function uuidv4() {
  // RFC 4122 version 4 compliant
  return ([1e7] + -1e3 + -4e3 + -8e3 + -1e11).replace(/[018]/g, (c) =>
    (
      c ^
      (crypto.getRandomValues(new Uint8Array(1))[0] & (15 >> (c / 4)))
    ).toString(16)
  );
}

const allAnswered = computed(() => {
  const susOk = Object.values(sus.value).every((v) => v >= 1 && v <= 5);
  const ethOk = Object.values(ethics.value).every((v) => v >= 1 && v <= 5);
  return susOk && ethOk;
});

function buildPayload() {
  const domain_specific = {};
  for (const item of domainItems.value) {
    if (item.label?.trim())
      domain_specific[item.label.trim()] = Number(item.value) || 0;
  }

  return {
    survey_id: uuidv4(),
    user_id: "anonymous",
    timestamp: new Date().toISOString(),
    pilot_tag: pilotTag.value,
    app_version: appVersion.value || "unknown",
    ai_model_version: aiModelVersion.value || "unknown",
    tam_sus_responses: { ...sus.value },
    ethics_responses: { ...ethics.value },
    domain_specific,
  };
}

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
    submitError.value = "Missing pilot_tag in URL.";
    return;
  }
  if (!consent.value) {
    submitError.value = "Please provide consent to proceed.";
    return;
  }

  submitting.value = true;
  try {
    const payload = buildPayload();
    const endpoint = import.meta.env.VITE_SURVEY_ENDPOINT || "/api/v1/survey";
    const res = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error(`Server responded ${res.status}`);
    submitOk.value = true;
    resetForm();
  } catch (e) {
    submitError.value = e?.message || "Submission failed.";
  } finally {
    submitting.value = false;
  }
}

function resetForm() {
  consent.value = false;
  for (const k of Object.keys(sus.value)) sus.value[k] = 0;
  for (const k of Object.keys(ethics.value)) ethics.value[k] = 0;
  domainItems.value = [];
}
</script>

<script>
// Local subcomponents (kept simple for portability)
export default {
  components: {
    QuestionRow: {
      props: { index: Number, label: String, modelValue: Number },
      emits: ["update:modelValue"],
      template: `
        <div class="mb-2">
          <div class="mb-1"><strong>{{ index }}.</strong> {{ label }}</div>
          <Likert :model-value="modelValue" @update:modelValue="$emit('update:modelValue', $event)" />
          <v-divider class="mt-4" />
        </div>
      `,
    },
    Likert: {
      props: { modelValue: Number },
      emits: ["update:modelValue"],
      data: () => ({ items: [1, 2, 3, 4, 5] }),
      template: `
        <div class="d-flex align-center gap-2">
          <span class="text-caption mr-2">1</span>
          <v-btn-toggle
            class="my-2"
            divided
            density="comfortable"
            :model-value="modelValue"
            @update:modelValue="$emit('update:modelValue', $event)"
          >
            <v-btn v-for="n in items" :key="n" :value="n">{{ n }}</v-btn>
          </v-btn-toggle>
          <span class="text-caption ml-2">5</span>
        </div>
      `,
    },
  },
};
</script>

<style scoped>
.gap-2 {
  gap: 0.5rem;
}
</style>
