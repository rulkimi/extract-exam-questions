import { createWebHistory, createRouter } from "vue-router";
import UploadPage from "@/views/UploadPage.vue";

const routes = [
  { path: '/', redirect: '/docs' },
  // { path: '/upload', component: UploadPage },
  {
    path: '/docs', component: () => import("@/views/documents/index.vue"),
    redirect: '/docs/list',
    children: [
      { path: 'list', component: () => import("@/views/documents/list.vue") },
      { path: 'upload', component: () => import("@/views/documents/upload.vue") },
    ]
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;