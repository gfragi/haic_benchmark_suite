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
import SimulatorPage from "@/views/SimulatorPage.vue";

const routes = [
  { path: "/", name: "home", component: HomeView },
  {
    path: "/about",
    name: "about", // route level code-splitting
    // this generates a separate chunk (about.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    component: AboutView,
  },
  {
    path: "/configs",
    name: "ConfigList",
    component: ConfigList,
  },
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
    name: "configForm",
    component: ConfigurationForm,
    props: { mode: "create" }, // This route is for creating a new configuration
  },
  {
    path: "/configuration/edit/:configId",
    name: "editConfigForm",
    component: ConfigurationForm,
    props: (route) => ({
      mode: "edit",
      configId: parseInt(route.params.configId),
    }), // This route is for editing an existing configuration
  },
  { path: "/log-generator", name: "LogGenerator", component: LogGenerator },
  { path: "/metrics", component: MetricsPage },
  {
    path: "/fairness",
    name: "Fairness Evaluation",
    component: FairnessEvaluation,
  },
  {
    path: "/survey-dashboard",
    name: "Survey Dashboard",
    component: SurveyDashboard,
  },
  {
    path: "/simulate",
    name: "Simulator",
    component: SimulatorPage,
    props: true,
  },
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

export default router;
