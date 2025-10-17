<template>
  <div class="qse">
    <v-alert type="info" variant="tonal" class="mb-3">
      Create a pilot-specific question set. Saving returns a
      <code>schema_id</code> that we auto-attach to the Public Survey link.
    </v-alert>

    <v-row class="mb-2">
      <v-col cols="12" md="6">
        <v-text-field
          label="Name"
          v-model="form.name"
          placeholder="SmartEnergy v1"
        />
      </v-col>
      <v-col cols="12" md="6">
        <v-text-field
          label="Pilot tag"
          v-model="form.pilot_tag"
          :readonly="!!pilotTag"
          :hint="pilotTag ? 'Prefilled from dashboard' : 'Optional'"
          persistent-hint
        />
      </v-col>
      <v-col cols="6" md="3">
        <v-text-field
          label="Version"
          v-model.number="form.version"
          type="number"
          min="1"
        />
      </v-col>
      <v-col cols="6" md="3" class="d-flex align-center">
        <v-switch v-model="form.active" label="Active" color="primary" inset />
      </v-col>
    </v-row>

    <div class="d-flex align-center mb-2">
      <div class="text-subtitle-2">Questions</div>
      <v-spacer />
      <v-btn
        size="small"
        variant="text"
        prepend-icon="mdi-plus"
        @click="addQuestion"
        >Add</v-btn
      >
    </div>

    <v-alert v-if="qError" type="warning" variant="tonal" class="mb-2">{{
      qError
    }}</v-alert>

    <v-card v-for="(q, i) in form.questions" :key="q._key" class="mb-3 pa-3">
      <div class="d-flex align-center mb-2">
        <div class="text-caption">#{{ i + 1 }}</div>
        <v-spacer />
        <v-btn icon="mdi-content-copy" variant="text" @click="dup(i)" />
        <v-btn icon="mdi-delete" variant="text" @click="del(i)" />
      </div>

      <v-row>
        <v-col cols="12" md="8">
          <v-text-field
            label="Label"
            v-model="q.label"
            @blur="maybeSlugId(q)"
          />
        </v-col>
        <v-col cols="12" md="4">
          <v-text-field
            label="ID"
            v-model="q.id"
            hint="Stable; used as column key"
            persistent-hint
          />
        </v-col>
        <v-col cols="12" md="4">
          <v-select
            label="Type"
            v-model="q.type"
            :items="types"
            item-title="label"
            item-value="value"
          />
        </v-col>
        <v-col cols="12" md="4">
          <v-text-field label="Group (section)" v-model="q.group" />
        </v-col>
        <v-col cols="12" md="4" class="d-flex align-center">
          <v-switch v-model="q.required" label="Required" inset />
        </v-col>

        <!-- Likert scale -->
        <template v-if="q.type === 'likert'">
          <v-col cols="6" md="3"
            ><v-text-field
              label="Min"
              type="number"
              v-model.number="q.scale.min"
          /></v-col>
          <v-col cols="6" md="3"
            ><v-text-field
              label="Max"
              type="number"
              v-model.number="q.scale.max"
          /></v-col>
          <v-col cols="12" md="3"
            ><v-text-field label="Min label" v-model="q.scale.min_label"
          /></v-col>
          <v-col cols="12" md="3"
            ><v-text-field label="Max label" v-model="q.scale.max_label"
          /></v-col>
        </template>

        <!-- Options for single/multi -->
        <template v-if="q.type === 'single' || q.type === 'multi'">
          <v-col cols="12">
            <v-combobox
              v-model="q.options"
              label="Options"
              multiple
              chips
              hint="Press Enter to add"
              persistent-hint
            />
          </v-col>
        </template>
      </v-row>
    </v-card>

    <div class="d-flex gap-2">
      <v-btn color="primary" :loading="saving" @click="save"
        >Save Question Set</v-btn
      >
      <v-btn variant="text" @click="reset">Reset</v-btn>
      <v-spacer />
      <v-btn variant="text" @click="exportJson">Export JSON</v-btn>
      <v-btn variant="text" @click="importJson">Import JSON</v-btn>
    </div>

    <v-alert v-if="saveMsg" :type="saveMsg.type" variant="tonal" class="mt-3">
      <template v-if="saveMsg.type === 'success'">
        Saved. schema_id: <code>{{ saveMsg.schema_id }}</code>
      </template>
      <template v-else>
        {{ saveMsg.text }}
      </template>
    </v-alert>
  </div>
</template>

<script setup>
import { ref, watch } from "vue";
import { createSchema } from "@/services/surveySchemas";

const props = defineProps({
  pilotTag: { type: String, default: "" },
});
const emit = defineEmits(["created", "error"]);

const types = [
  { label: "Likert (1–5)", value: "likert" },
  { label: "Single choice", value: "single" },
  { label: "Multi choice", value: "multi" },
  { label: "Text", value: "text" },
  { label: "Number", value: "number" },
  { label: "Boolean", value: "boolean" },
];

const form = ref({
  name: "",
  pilot_tag: props.pilotTag || "",
  version: 1,
  active: true,
  questions: [],
});

watch(
  () => props.pilotTag,
  (v) => {
    if (v && !form.value.pilot_tag) form.value.pilot_tag = v;
  }
);

const qError = ref("");
const saving = ref(false);
const saveMsg = ref(null);

function newQuestion() {
  return {
    _key: crypto.randomUUID?.() || Math.random().toString(36).slice(2),
    id: "",
    label: "",
    type: "likert",
    required: false,
    group: "",
    scale: {
      min: 1,
      max: 5,
      min_label: "Strongly disagree",
      max_label: "Strongly agree",
    },
    options: [],
  };
}
function addQuestion() {
  form.value.questions.push(newQuestion());
}
function dup(i) {
  const q = form.value.questions[i];
  const copy = JSON.parse(JSON.stringify(q));
  copy._key = crypto.randomUUID?.() || Math.random().toString(36).slice(2);
  copy.id = `${q.id || "q"}_copy`;
  form.value.questions.splice(i + 1, 0, copy);
}
function del(i) {
  form.value.questions.splice(i, 1);
}

function slug(s) {
  return String(s || "")
    .toLowerCase()
    .trim()
    .replace(/\s+/g, "_")
    .replace(/[^\w-]/g, "");
}
function maybeSlugId(q) {
  if (!q.id && q.label) q.id = slug(q.label);
}

function validate() {
  qError.value = "";
  if (!form.value.name) {
    qError.value = "Name is required.";
    return false;
  }
  if (!form.value.questions.length) {
    qError.value = "Add at least one question.";
    return false;
  }
  const ids = new Set();
  for (const q of form.value.questions) {
    if (!q.id) {
      qError.value = "Every question needs an ID.";
      return false;
    }
    if (ids.has(q.id)) {
      qError.value = `Duplicate ID: ${q.id}`;
      return false;
    }
    ids.add(q.id);
    if (q.type === "likert") {
      if (
        !(
          q.scale &&
          Number.isFinite(q.scale.min) &&
          Number.isFinite(q.scale.max) &&
          q.scale.min < q.scale.max
        )
      ) {
        qError.value = `Invalid Likert scale for ${q.id}`;
        return false;
      }
    }
    if (
      (q.type === "single" || q.type === "multi") &&
      (!q.options || !q.options.length)
    ) {
      qError.value = `Provide options for ${q.id}`;
      return false;
    }
  }
  return true;
}

async function save() {
  if (!validate()) return;
  saving.value = true;
  saveMsg.value = null;
  try {
    const payload = {
      name: form.value.name,
      pilot_tag: form.value.pilot_tag || null,
      version: form.value.version || 1,
      active: !!form.value.active,
      questions: form.value.questions.map((q) => {
        const rest = { ...q };
        delete rest._key;
        if (!rest.group) rest.group = null;
        if (!rest.options?.length) rest.options = null;
        if (rest.type !== "likert") rest.scale = null;
        return rest;
      }),
    };
    console.log("[QuestionSetEditor] POST /survey/schemas payload:", payload);

    const out = await createSchema(payload);
    console.log("[QuestionSetEditor] schema created:", out);

    saveMsg.value = { type: "success", schema_id: out.schema_id };
    emit("created", out); // let parent auto-fill schema_id in link
  } catch (e) {
    console.error("[QuestionSetEditor] save failed:", e);
    saveMsg.value = { type: "error", text: e?.message || "Failed to save." };
    +emit("error", e);
  } finally {
    saving.value = false;
  }
}

function reset() {
  form.value = {
    name: "",
    pilot_tag: props.pilotTag || "",
    version: 1,
    active: true,
    questions: [],
  };
  qError.value = "";
  saveMsg.value = null;
}

function exportJson() {
  const data = {
    name: form.value.name,
    pilot_tag: form.value.pilot_tag || null,
    version: form.value.version || 1,
    active: !!form.value.active,
    questions: form.value.questions.map((q) => {
      const clone = { ...q };
      delete clone._key;
      return clone;
    }),
  };
  const blob = new Blob([JSON.stringify(data, null, 2)], {
    type: "application/json",
  });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "question_set.json";
  a.click();
}

function importJson() {
  const input = document.createElement("input");
  input.type = "file";
  input.accept = "application/json";
  input.onchange = (e) => {
    const f = e.target.files?.[0];
    if (!f) return;
    const reader = new FileReader();
    reader.onload = () => {
      try {
        const obj = JSON.parse(reader.result);
        form.value.name = obj.name || "";
        form.value.pilot_tag = obj.pilot_tag || form.value.pilot_tag;
        form.value.version = obj.version || 1;
        form.value.active = obj.active ?? true;
        form.value.questions = (obj.questions || []).map((q) => ({
          _key: crypto.randomUUID?.() || Math.random().toString(36).slice(2),
          ...q,
        }));
      } catch (e) {
        qError.value = "Invalid JSON.";
      }
    };
    reader.readAsText(f);
  };
  input.click();
}
</script>

<style scoped>
.qse :deep(.v-combobox .v-field__input) {
  min-height: 40px;
}
.gap-2 {
  gap: 0.5rem;
}
</style>
