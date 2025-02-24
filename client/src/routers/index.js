import { createWebHistory, createRouter } from "vue-router";
import UploadPage from "@/views/upload-page.vue";

const routes = [
  { path: '/', redirect: '/upload' },
  { path: '/upload', component: UploadPage }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;