import { createWebHistory, createRouter } from "vue-router";
import UploadPage from "@/views/UploadPage.vue";

const routes = [
  { path: '/', redirect: '/upload' },
  { path: '/upload', component: UploadPage }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;