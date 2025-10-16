import { createWebHashHistory, createRouter } from "vue-router";
import BaseLayout from '@/layouts/BaseLayout.vue';

const routes = [
  {
    path: '/',
    component: BaseLayout,
    redirect: '/list',
    children: [
      { path: 'list', name: 'doc-list', component: () => import("@/views/documents/list.vue") },
      { path: ':id', name: 'doc-detail', component: () => import("@/views/documents/detail.vue"), props: route => ({ id: route.params.id }) },
      { path: 'settings', name: 'doc-settings', component: () => import("@/views/settings.vue") }
    ]
  },
  { path: '/landing', name: 'landing', component: () => import("@/views/landing.vue") },
  { path: '/signin', name: 'signin', component: () => import("@/views/auth/signin.vue")},
  { path: '/signup', name: 'signup', component: () => import("@/views/auth/signup.vue")},
];

const router = createRouter({
  history: createWebHashHistory(),
  routes,
});

export default router;