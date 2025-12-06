import { createRouter, createWebHistory } from "vue-router";
import HomeView from "@/views/HomeView.vue";
import ConfigList from "@/views/ConfigList.vue";
import LogManagement from "@/components/LogManagement.vue";
import ResultDetail from "@/views/ResultDetail.vue";
import EvaluationReports from "@/views/EvaluationReports.vue";
import ConfigurationForm from "@/components/ConfigurationForm.vue";
import AboutView from "@/views/AboutView.vue";
import LogGenerator from "@/components/LogGenerator.vue";
import MetricsPage from "@/components/MetricsPage.vue";
import LogUploadForm from "@/components/LogIngestionForm.vue";
import RunDetail from "@/views/RunDetail.vue";
import Visualization from "@/views/VisualizationPage.vue";
import FairnessEvaluation from "@/views/FairnessEvaluation.vue";
import SurveyDashboard from "@/views/SurveyDashboard.vue";
import EnvBuilderPage from "@/views/EnvBuilderPage.vue";
import SimulatorPage from "@/views/SimulatorPage.vue";
import SurveyCompare from "@/views/SurveyCompare.vue";
// import keycloak from "@/services/keycloak";
import PublicSurvey from "@/views/PublicSurvey.vue";

const routes = [
  { path: "/", name: "Home", component: HomeView, meta: { public: true } },
  {
    path: "/about",
    name: "About",
    component: AboutView,
    meta: { public: true },
  },

  { path: "/configs", name: "ConfigList", component: ConfigList },
  { path: "/logs", name: "LogManagement", component: LogManagement },
  { path: "/logs/upload", name: "LogUploadForm", component: LogUploadForm },

  {
    path: "/results/:configId",
    name: "ResultDetail",
    component: ResultDetail,
    props: true,
  },
  {
    path: "/results/:configId/:runId",
    name: "RunDetail",
    component: RunDetail,
    props: true,
  },
  {
    path: "/results/:configId/plot",
    name: "Visualization",
    component: Visualization,
  },

  { path: "/reports", name: "EvaluationReports", component: EvaluationReports },

  {
    path: "/configuration/new",
    name: "ConfigForm",
    component: ConfigurationForm,
    props: { mode: "create" },
  },
  {
    path: "/configuration/edit/:configId",
    name: "EditConfigForm",
    component: ConfigurationForm,
    props: (route) => ({
      mode: "edit",
      configId: parseInt(route.params.configId),
    }),
  },

  { path: "/log-generator", name: "LogGenerator", component: LogGenerator },
  {
    path: "/metrics",
    name: "Metrics",
    component: MetricsPage,
    meta: { public: true },
  },

  {
    path: "/fairness",
    name: "FairnessEvaluation",
    component: FairnessEvaluation,
  },
  {
    path: "/survey-dashboard",
    name: "SurveyDashboard",
    component: SurveyDashboard,
  },
  {
    path: "/env-builder",
    name: "EnvBuilder",
    component: EnvBuilderPage,
  },
  {
    path: "/simulate",
    name: "Simulator",
    component: SimulatorPage,
    props: true,
  },

  { path: "/survey-compare", name: "SurveyCompare", component: SurveyCompare },

  {
    path: "/survey",
    name: "PublicSurvey",
    component: PublicSurvey,
    props: true,
    meta: { public: true },
  },

  { path: "/:pathMatch(.*)*", redirect: "/" },
];

const router = createRouter({
  history: createWebHistory(
    import.meta?.env?.BASE_URL || process.env.BASE_URL || "/"
  ),
  routes,
});

router.beforeEach((to) => {
  if (to.meta.public) return true;
  const isAuthed = !!window.__kc?.authenticated;
  if (!isAuthed) {
    window.__kc?.login(); // send to Keycloak
    return false; // cancel current navigation
  }
  return true;
});

export default router;
