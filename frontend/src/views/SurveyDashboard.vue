<template>
  <BaseLayout>
    <v-container>
      <v-row class="gap-y-4">
        <!-- LEFT: Controls rail (sticky) -->
        <v-col cols="12" md="3">
          <v-card class="pa-4 control-rail">
            <div class="text-subtitle-2 mb-2">
              SUS &amp; Ethics
              <span v-if="selectedPilotTag" class="text-caption ml-1"
                >· {{ selectedPilotTag }}</span
              >
            </div>

            <!-- Mode -->
            <div class="mb-3">
              <div class="text-caption text-medium-emphasis mb-1">Mode</div>
              <v-btn-toggle
                v-model="comparisonMode"
                mandatory
                rounded
                density="comfortable"
                class="w-100"
              >
                <v-btn value="versions">Versions</v-btn>
                <v-btn value="pilots">Pilots</v-btn>
              </v-btn-toggle>
            </div>

            <!-- Pilot selector (Versions only) -->
            <div v-if="comparisonMode === 'versions'" class="mb-3">
              <div class="text-caption text-medium-emphasis mb-1">Pilot</div>
              <SurveyFilter @update:pilotTag="loadData" />
            </div>

            <!-- Chart type -->
            <div class="mb-3">
              <div class="text-caption text-medium-emphasis mb-1">Chart</div>
              <v-btn block variant="tonal" @click="toggleChartType">
                <v-icon start>{{
                  isLineChart ? "mdi-chart-line" : "mdi-chart-bar"
                }}</v-icon>
                {{ isLineChart ? "Line" : "Bar" }}
              </v-btn>
            </div>

            <v-divider class="my-3" />

            <!-- Actions -->
            <v-btn
              block
              color="primary"
              class="mb-2"
              @click="openShare"
              :disabled="comparisonMode === 'versions' && !selectedPilotTag"
            >
              <v-icon start>mdi-link-variant</v-icon>
              Build Link
            </v-btn>

            <v-btn
              block
              variant="outlined"
              class="mb-2"
              :disabled="!selectedPilotTag"
              @click="goCompare"
            >
              <v-icon start>mdi-compare</v-icon>
              Compare Versions
            </v-btn>

            <v-btn block variant="text" class="mb-1" @click="exportData">
              <v-icon start>mdi-download</v-icon>
              Export CSV
            </v-btn>

            <v-btn block variant="text" @click="refresh">
              <v-icon start>mdi-refresh</v-icon>
              Refresh
            </v-btn>

            <v-divider class="my-3" />

            <div class="text-caption text-medium-emphasis">
              Tip: In <em>Versions</em>, pick a pilot and compare app versions.
              In <em>Pilots</em>, compare across pilots.
            </div>
          </v-card>
        </v-col>

        <!-- RIGHT: Chart & content -->
        <v-col cols="12" md="9">
          <!-- Loading -->
          <div v-if="loading" class="text-center my-8">
            <v-progress-circular indeterminate color="primary" size="40" />
          </div>

          <!-- Chart header -->
          <div v-else class="text-center my-4">
            <h3 class="text-h6">{{ chartTitle }}</h3>
            <div class="text-caption">Total surveys: {{ totalSurveys }}</div>
            <div class="text-caption text-medium-emphasis mt-1">
              SUS and Ethics are shown on a 0–100 scale (higher is better).
              Hover for exact values and counts.
            </div>
          </div>

          <!-- Chart -->
          <SurveyChart
            v-if="Object.keys(aggregatedData).length"
            :data="sortedAggregatedData"
            :type="chartType"
            :x-label="comparisonMode === 'versions' ? 'App Version' : 'Pilot'"
            y-label="Average score (0–100)"
            :legend-info="true"
          />

          <!-- Empty state -->
          <div v-else class="text-center my-8">
            <p>No data available.</p>
          </div>

          <!-- Reference panels -->
          <v-expansion-panels class="mt-6">
            <v-expansion-panel>
              <v-expansion-panel-title>SUS Questions</v-expansion-panel-title>
              <v-expansion-panel-text>
                <ol>
                  <li>I think I would like to use this system frequently.</li>
                  <li>I found the system unnecessarily complex.</li>
                  <li>I thought the system was easy to use.</li>
                  <li>
                    I think I would need the support of a technical person to
                    use this system.
                  </li>
                  <li>
                    I found the various functions in this system were well
                    integrated.
                  </li>
                  <li>
                    I thought there was too much inconsistency in this system.
                  </li>
                  <li>
                    I would imagine most people would learn to use this system
                    quickly.
                  </li>
                  <li>I found the system very difficult to use.</li>
                  <li>I felt very confident using the system.</li>
                  <li>
                    I needed to learn many things before I could get going with
                    this system.
                  </li>
                </ol>
              </v-expansion-panel-text>
            </v-expansion-panel>
            <v-expansion-panel>
              <v-expansion-panel-title
                >Ethics Questions</v-expansion-panel-title
              >
              <v-expansion-panel-text>
                <ol>
                  <li>
                    Fairness: The system handles different tasks or users
                    without bias.
                  </li>
                  <li>
                    Transparency: I understand how the system/AI arrives at its
                    decisions.
                  </li>
                  <li>
                    Privacy: I feel confident that personal data is protected.
                  </li>
                  <li>
                    Accountability: It is clear who or what is responsible for
                    errors.
                  </li>
                  <li>
                    Trust: Overall, I trust the system to operate ethically and
                    in my best interest.
                  </li>
                </ol>
              </v-expansion-panel-text>
            </v-expansion-panel>
          </v-expansion-panels>
        </v-col>
      </v-row>

      <!-- Share dialog (Build Link pop-out) -->
      <v-dialog v-model="shareOpen" max-width="640">
        <v-card>
          <v-card-title>Public Survey Link</v-card-title>
          <v-card-text>
            <div class="mb-2">
              Share this link with pilot users to answer directly:
            </div>

            <v-row class="mb-2">
              <v-col cols="12" md="6">
                <v-text-field
                  label="Pilot"
                  :model-value="selectedPilotTag || '—'"
                  prepend-inner-icon="mdi-tag-outline"
                  readonly
                />
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  label="App version (prefill)"
                  v-model="selectedAppVersion"
                  prepend-inner-icon="mdi-application-cog"
                />
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  label="AI model version (prefill)"
                  v-model="selectedModelVersion"
                  prepend-inner-icon="mdi-robot-outline"
                />
              </v-col>
            </v-row>

            <v-text-field
              :model-value="surveyHref"
              readonly
              prepend-inner-icon="mdi-link-variant"
              append-inner-icon="mdi-content-copy"
              @click:append-inner="copy(surveyHref)"
            />

            <div
              class="my-4"
              style="display: flex; gap: 16px; align-items: center"
            >
              <v-img
                :src="qrDataUrl"
                width="140"
                height="140"
                alt="Survey QR"
                class="rounded"
              />
              <div class="text-body-2">
                Scan to open the survey on mobile.
                <div class="mt-2">
                  <v-btn size="small" variant="outlined" @click="downloadQR">
                    <v-icon start>mdi-download</v-icon> Download QR
                  </v-btn>
                </div>
              </div>
            </div>
            <div class="text-caption text-medium-emphasis mt-4 mb-1">
              Question set
            </div>
            <v-switch
              v-model="autoAttachLatest"
              color="primary"
              inset
              label="Auto-attach latest for selected pilot"
            />
            <v-text-field
              v-model="selectedSchemaId"
              label="schema_id (optional)"
              :hint="
                autoAttachLatest
                  ? 'Auto-filled when available; you can override.'
                  : 'Paste a schema_id to pin a specific version.'
              "
              persistent-hint
              prepend-inner-icon="mdi-identifier"
            />
            <v-alert type="info" variant="tonal">
              You can also append <code>&amp;app_version=...</code> and
              <code>&amp;ai_model_version=...</code> to prefill metadata.
            </v-alert>
          </v-card-text>
          <v-card-actions>
            <v-spacer />
            <v-btn variant="text" :href="surveyHref" target="_blank"
              >Open</v-btn
            >
            <v-btn variant="flat" color="primary" @click="copy(surveyHref)"
              >Copy</v-btn
            >
            <v-btn variant="text" @click="shareOpen = false">Close</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </v-container>
  </BaseLayout>
</template>

<script setup>
import BaseLayout from "@/components/BaseLayout.vue";
import SurveyFilter from "@/components/SurveyFilter.vue";
import SurveyChart from "@/components/SurveyChart.vue";
import { fetchSurveyAggregates } from "@/services/survey";
import { ref, computed, watch } from "vue";
import { useRouter } from "vue-router";
import debounce from "lodash.debounce";
import semver from "semver";
import QRCode from "qrcode";
import { fetchLatestSchemaForPilot } from "@/services/surveySchemas";

const selectedSchemaId = ref("");
const autoAttachLatest = ref(true);

const comparisonMode = ref("versions");
const aggregatedData = ref({});
const loading = ref(false);
const isLineChart = ref(false);
const chartType = computed(() => (isLineChart.value ? "line" : "bar"));
const shareOpen = ref(false);
const qrDataUrl = ref("");
const selectedAppVersion = ref("");
const selectedModelVersion = ref("");
const selectedPilotTag = ref("");
const router = useRouter();

const surveyHref = computed(() => {
  const origin = window.location.origin;
  const query = {
    pilot_tag: selectedPilotTag.value || undefined,
    app_version: selectedAppVersion.value || undefined,
    ai_model_version: selectedModelVersion.value || undefined,
    schema_id: (selectedSchemaId.value || "").trim() || undefined, // NEW
  };
  const href = router.resolve({ name: "PublicSurvey", query }).href;
  return `${origin}${href}`;
});

// const surveyHref = computed(() => {
//   const href = router.resolve({
//     name: "PublicSurvey",
//     query: {
//       pilot_tag: selectedPilotTag.value || undefined,
//       app_version: selectedAppVersion.value || undefined,
//       ai_model_version: selectedModelVersion.value || undefined,
//     },
//   }).href;

//   const hash = new URLSearchParams({
//     pilot_tag: selectedPilotTag.value || "",
//     app_version: selectedAppVersion.value || "",
//     ai_model_version: selectedModelVersion.value || "",
//   }).toString();

//   return `${window.location.origin}${href}#${hash}`;
// });

const totalSurveys = computed(() =>
  Object.values(aggregatedData.value).reduce(
    (acc, val) => acc + (val.count || 0),
    0
  )
);

const chartTitle = computed(() => {
  if (comparisonMode.value === "versions") {
    return `Avg SUS & Ethics per App Version for "${
      selectedPilotTag.value || "..."
    }"`;
  } else {
    return "Avg SUS & Ethics per Pilot";
  }
});

const sortedAggregatedData = computed(() => {
  const entries = Object.entries(aggregatedData.value);
  if (comparisonMode.value === "versions") {
    return Object.fromEntries(
      entries.sort(([a], [b]) => {
        if (semver.valid(a) && semver.valid(b)) {
          return semver.compare(a, b);
        }
        return a.localeCompare(b); // fallback
      })
    );
  }
  return aggregatedData.value;
});

const loadData = debounce(async (pilotTag = null) => {
  loading.value = true;
  try {
    selectedPilotTag.value = pilotTag;
    const raw = await fetchSurveyAggregates(
      comparisonMode.value === "versions" ? pilotTag : null
    );
    aggregatedData.value = raw;
  } catch (error) {
    console.error("Failed to load data:", error);
    aggregatedData.value = {};
  } finally {
    loading.value = false;
  }
}, 300);

// Initial load: default is all pilots
loadData();

function exportData() {
  const csv = Object.entries(aggregatedData.value)
    .map(
      ([key, vals]) =>
        `${key},${vals.avg_sus.toFixed(2)},${vals.avg_ethics.toFixed(2)},${
          vals.count
        }`
    )
    .join("\n");

  const header =
    comparisonMode.value === "versions"
      ? "App Version,Avg SUS,Avg Ethics,Count\n"
      : "Pilot,Avg SUS,Avg Ethics,Count\n";

  const blob = new Blob([header + csv], { type: "text/csv" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = "survey_aggregates.csv";
  link.click();
}

function goCompare() {
  // opens the compare page with the current pilot preselected
  router.push({
    name: "SurveyCompare",
    query: { pilot: selectedPilotTag.value || "" },
  });
}

function refresh() {
  // reload current mode (pilot-level or version-level)
  loadData(selectedPilotTag.value || null);
}

function toggleChartType() {
  isLineChart.value = !isLineChart.value;
}

// function slug(s) {
//   return String(s || "")
//     .trim()
//     .replace(/\s+/g, "-") // spaces -> dashes
//     .replace(/[^\w-]/g, ""); // strip odd chars
// }

// const publicLink = computed(() => {
//   const pilot = slug(selectedPilotTag.value);
//   const base = pilot
//     ? `${window.location.origin}/survey/:pilot_tag?${encodeURIComponent(pilot)}`
//     : `${window.location.origin}/survey`;
//   const params = new URLSearchParams();
//   if (selectedAppVersion.value)
//     params.set("app_version", selectedAppVersion.value);
//   if (selectedModelVersion.value)
//     params.set("ai_model_version", selectedModelVersion.value);
//   const qs = params.toString();
//   return qs ? `${base}?${qs}` : base;
// });

watch(surveyHref, async (url) => {
  try {
    qrDataUrl.value = await QRCode.toDataURL(url, { margin: 1, scale: 5 });
  } catch (e) {
    console.error("QR gen error:", e);
  }
});

watch(
  [shareOpen, selectedPilotTag, autoAttachLatest],
  async ([open, pilot, auto]) => {
    if (!open || !auto || !pilot) return;
    try {
      const latest = await fetchLatestSchemaForPilot(pilot);
      selectedSchemaId.value = latest?.schema_id || "";
    } catch (e) {
      console.error("Failed to fetch pilot schema:", e);
      selectedSchemaId.value = "";
    }
  }
);

function openShare() {
  shareOpen.value = true;
  // ensure QR exists if dialog opened before computed ran
  QRCode.toDataURL(surveyHref.value, { margin: 1, scale: 5 })
    .then((d) => {
      qrDataUrl.value = d;
    })
    .catch((e) => console.error("QR gen error:", e));
}

function downloadQR() {
  const a = document.createElement("a");
  a.href = qrDataUrl.value;
  a.download = `survey_link_${selectedPilotTag.value || "pilot"}.png`;
  a.click();
}

async function copy(text) {
  try {
    await navigator.clipboard.writeText(text);
  } catch (err) {
    console.error("Clipboard copy failed:", err); // handle or report
  }
}
</script>

<style scoped>
.control-rail {
  position: sticky;
  top: 72px; /* adjust if your app bar height differs */
}
</style>
