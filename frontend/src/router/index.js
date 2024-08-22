import { createRouter, createWebHistory } from "vue-router";
import HomeView from "@/views/HomeView.vue";
import EvaluationConfigList from "@/views/EvaluationConfigList.vue";
import LogIngestion from "@/views/LogIngestion.vue";
import EvaluationResults from "@/views/EvaluationResults.vue";
import EvaluationReports from "@/views/EvaluationReports.vue";
import ConfigurationForm from "@/components/ConfigurationForm.vue";
import AboutView from "@/views/AboutView.vue";

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
  { path: "/logs", name: "LogIngestion", component: LogIngestion },
  { path: "/results", name: "EvaluationResults", component: EvaluationResults },
  { path: "/reports", name: "EvaluationReports", component: EvaluationReports },
  {
    path: "/configuration/new",
    name: "configForm",
    component: ConfigurationForm,
  },
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

export default router;
