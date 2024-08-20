import { createRouter, createWebHistory } from "vue-router";
import HomeView from "../views/HomeView.vue";
import EvaluationConfigList from "@/views/EvaluationConfigList.vue";
import LogIngestion from "@/views/LogIngestion.vue";
import EvaluationResults from "@/views/EvaluationResults.vue";
import EvaluationReports from "@/views/EvaluationReports.vue";
import EvaluationConfigForm from "@/components/EvaluationConfigForm.vue";

const routes = [
  { path: "/", name: "home", component: HomeView },
  {
    path: "/about",
    name: "about", // route level code-splitting
    // this generates a separate chunk (about.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    component: () =>
      import(/* webpackChunkName: "about" */ "../views/AboutView.vue"),
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
    path: "/configs/new",
    name: "configForm",
    component: EvaluationConfigForm,
  },
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

export default router;
