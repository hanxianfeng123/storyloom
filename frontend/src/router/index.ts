import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('../pages/ProjectList.vue'),
    },
    {
      path: '/project/:id',
      name: 'project-detail',
      component: () => import('../pages/ProjectDetail.vue'),
    },
    {
      path: '/project/:id/pipeline',
      name: 'pipeline-run',
      component: () => import('../pages/PipelineRun.vue'),
    },
    {
      path: '/project/:id/memory',
      name: 'memory-explorer',
      component: () => import('../pages/MemoryExplorer.vue'),
    },
    {
      path: '/project/:id/skills',
      name: 'skill-editor',
      component: () => import('../pages/SkillEditor.vue'),
    },
  ],
})

export default router
