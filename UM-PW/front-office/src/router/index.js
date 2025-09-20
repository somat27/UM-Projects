import { createRouter, createWebHistory } from "vue-router";
import MainPage from "@/views/MainPage.vue";
import AboutUS from "@/views/AboutUS.vue";
import Help from "@/views/Help.vue";
import Report from "@/views/Report.vue";
import Ocorrencias from "@/views/Ocurrence.vue";
import Mapa from "@/views/Map.vue";
import Social from "@/views/Social.vue";
import Feedback from "@/views/Feedback.vue";

const routes = [
  {
    path: "/",
    name: "Home",
    component: MainPage,
  },
  {
    path: "/sobre-nos",
    name: "AboutUS",
    component: AboutUS,
  },
  {
    path: "/help",
    name: "Help",
    component: Help,
  },
  {
    path: "/report",
    name: "Report",
    component: Report,
    props: (route) => ({ defaultCategory: route.query.category || "" }),
  },
  {
    path: "/ocorrencias",
    name: "Ocorrencias",
    component: Ocorrencias,
  },
  {
    path: "/mapa",
    name: "Mapa",
    component: Mapa,
  },
  {
    path: "/social",
    name: "Social",
    component: Social,
  },
  {
    path: "/feedback",
    name: "Feedback",
    component: Feedback,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 };
  },
});

export default router;
