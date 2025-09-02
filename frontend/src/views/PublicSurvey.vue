<template>
  <BaseLayout>
    <v-container class="py-8" max-width="900">
      <v-card rounded="xl" elevation="2">
        <v-toolbar flat>
          <v-toolbar-title>User Feedback Survey (SUS + Ethics)</v-toolbar-title>
          <v-spacer />
          <v-chip color="primary" variant="flat">{{
            pilotTag || "No pilot selected"
          }}</v-chip>
        </v-toolbar>
        <v-divider />

        <v-card-text>
          <v-alert type="info" variant="tonal" class="mb-4">
            Please rate each statement from 1 (Strongly Disagree) to 5 (Strongly
            Agree).
          </v-alert>

          <v-form v-model="valid" @submit.prevent="submit">
            <v-row>
              <v-col cols="12" md="4">
                <v-text-field
                  label="Pilot tag"
                  v-model="pilotTag"
                  :disabled="!!$route.params.pilot"
                  required
                />
              </v-col>
              <v-col cols="12" md="4">
                <v-text-field
                  label="App version (optional)"
                  v-model="appVersion"
                />
              </v-col>
              <v-col cols="12" md="4">
                <v-text-field
                  label="AI model version (optional)"
                  v-model="aiModelVersion"
                />
              </v-col>
            </v-row>

            <v-divider class="my-6" />

            <v-subheader class="text-h6 mb-2">SUS Questions</v-subheader>
            <div v-for="q in susQuestions" :key="q.key" class="mb-3">
              <div class="mb-1 font-medium">{{ q.label }}</div>
              <v-radio-group
                v-model="sus[q.key]"
                inline
                :rules="[(v) => !!v || 'Required']"
              >
                <v-radio
                  v-for="i in 5"
                  :key="i"
                  :label="likertLabels[i - 1]"
                  :value="i"
                />
              </v-radio-group>
            </div>

            <v-divider class="my-6" />

            <v-subheader class="text-h6 mb-2">Ethics Questions</v-subheader>
            <div v-for="q in ethicsQuestions" :key="q.key" class="mb-3">
              <div class="mb-1 font-medium">{{ q.label }}</div>
              <v-radio-group
                v-model="ethics[q.key]"
                inline
                :rules="[(v) => !!v || 'Required']"
              >
                <v-radio
                  v-for="i in 5"
                  :key="i"
                  :label="likertLabels[i - 1]"
                  :value="i"
                />
              </v-radio-group>
            </div>

            <v-divider class="my-6" />

            <v-btn
              :loading="loading"
              color="primary"
              type="submit"
              :disabled="!valid"
            >
              <v-icon start>mdi-send</v-icon> Submit
            </v-btn>
          </v-form>
        </v-card-text>
      </v-card>

      <v-snackbar v-model="snack.show" :timeout="4000" :color="snack.color">
        {{ snack.text }}
      </v-snackbar>
    </v-container>
  </BaseLayout>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";
import axios from "@/services/axios";
import { useRoute } from "vue-router";

const valid = ref(false);
const loading = ref(false);
const snack = reactive({ show: false, text: "", color: "success" });

const likertLabels = ["1", "2", "3", "4", "5"]; // keep simple; you can show SD..SA if you prefer

const routeParams = useRoute().params;
const query = useRoute().query;

const pilotTag = ref(routeParams.pilot || (query.pilot ?? ""));
const appVersion = ref(query.app_version ?? "");
const aiModelVersion = ref(query.model_version ?? "");

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
      "I think that I would need the support of a technical person to use this system.",
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
  { key: "sus_q8", label: "I found the system very difficult to use." },
  { key: "sus_q9", label: "I felt very confident using the system." },
  {
    key: "sus_q10",
    label:
      "I needed to learn many things before I could get going with this system.",
  },
];

const ethicsQuestions = [
  {
    key: "q_fairness",
    label:
      "Fairness: The system handles different tasks/users/data without bias.",
  },
  {
    key: "q_transparency",
    label:
      "Transparency: I understand how the system arrives at its decisions.",
  },
  {
    key: "q_privacy",
    label: "Privacy: Sensitive or personal data is protected.",
  },
  {
    key: "q_accountability",
    label: "Accountability: It is clear who is responsible if the system errs.",
  },
  {
    key: "q_trust",
    label: "Trust: Overall, I trust this system to act in my best interest.",
  },
];

const sus = reactive({});
const ethics = reactive({});

function uuid4() {
  // lightweight client UUID; backend also has one but this is fine to send as user_id
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (c) => {
    const r = crypto.getRandomValues(new Uint8Array(1))[0] & 15;
    const v = c === "x" ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}
const userId = uuid4();

async function submit() {
  loading.value = true;
  try {
    const payload = {
      user_id: userId,
      pilot_tag: pilotTag.value,
      app_version: appVersion.value || null,
      ai_model_version: aiModelVersion.value || null,
      tam_sus_responses: sus,
      ethics_responses: ethics,
      domain_specific: null,
    };
    // matches your FastAPI route (adjust base path if you mount it under /api/surveys)
    await axios.post("/survey", payload);
    snack.text = "Thanks! Your response was recorded.";
    snack.color = "success";
    snack.show = true;
    // optionally route to a thank-you page
  } catch (e) {
    snack.text = "Submission failed. Please try again.";
    snack.color = "error";
    snack.show = true;
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  // if the pilot is fixed in the URL, keep it disabled to avoid user error
});
</script>
