import { createWebHistory, createRouter } from "vue-router";

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
  },
  { path: '/playground', component: () => import("@/views/playground.vue") }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;