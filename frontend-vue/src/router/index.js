import { createRouter, createWebHistory } from 'vue-router'
import AdminView from '../views/AdminView.vue'
import PublicFormView from '../views/PublicFormView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'admin',
      component: AdminView
    },
    {
      path: '/f/:formId',
      name: 'publicForm',
      component: PublicFormView
    }
  ]
})

export default router
