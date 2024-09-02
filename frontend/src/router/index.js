import { createRouter, createWebHistory } from "vue-router";
import HomeView from "@/views/HomeView.vue";
import EvaluationConfigList from "@/views/EvaluationConfigList.vue";
import LogManagement from "@/components/LogManagement.vue";
import EvaluationResultsList from "@/views/EvaluationResultsList.vue";
import EvaluationResultDetail from "@/views/EvaluationResultDetail.vue";
import EvaluationReports from "@/views/EvaluationReports.vue";
import ConfigurationForm from "@/components/ConfigurationForm.vue";
import AboutView from "@/views/AboutView.vue";
import LogGenerator from "@/components/LogGenerator.vue";
import MetricsPage from "@/components/MetricsPage.vue";
import ResultPlot from "@/components/ResultView.vue";

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
    name: "EvaluationConfigList",
    component: EvaluationConfigList,
  },
  { path: "/logs", name: "LogManagement", component: LogManagement },
  {
    path: "/results",
    name: "EvaluationResultsList",
    component: EvaluationResultsList,
  },
  {
    path: "/results/:configId",
    name: "ResultDetail",
    component: EvaluationResultDetail,
    props: true,
  },
  {
    path: "/results/::configId/view",
    name: "ResultPlot",
    component: ResultPlot,
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
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

export default router;
