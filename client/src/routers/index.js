import { createWebHistory, createRouter } from "vue-router";
import UploadPage from "@/views/UploadPage.vue";

const routes = [
  { path: '/', redirect: '/docs' },
  // { path: '/upload', component: UploadPage },
  { path: '/docs', component: () => import("@/views/Documents.vue")}
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;