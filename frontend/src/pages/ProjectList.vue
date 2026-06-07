<template>
  <div class="project-list-page">
    <div class="page-header animate-in">
      <h1>Projects</h1>
      <button class="btn btn-primary" @click="showForm = true" v-if="!showForm">
        + New Project
      </button>
    </div>

    <div v-if="showForm" class="create-form animate-in animate-in-delay-1">
      <input
        v-model="newName"
        placeholder="Project name"
        @keyup.enter="createProject"
        @keyup.escape="showForm = false"
        autofocus
      />
      <button class="btn btn-primary" @click="createProject" :disabled="!newName.trim()">
        Create
      </button>
      <button class="btn btn-ghost" @click="showForm = false">Cancel</button>
    </div>

    <div v-if="loading" class="loading-state">
      <p>Loading projects...</p>
    </div>

    <div v-else-if="error" class="error-state">
      <p>{{ error }}</p>
      <button class="btn btn-ghost" @click="fetchProjects">Retry</button>
    </div>

    <div v-else-if="projects.length === 0" class="empty-state animate-in animate-in-delay-1">
      <div class="empty-icon">✎</div>
      <h3>No projects yet</h3>
      <p>Create your first novel project to get started.</p>
    </div>

    <div v-else class="project-grid">
      <router-link
        v-for="(project, i) in projects"
        :key="project.id"
        :to="`/project/${project.id}`"
        class="project-card card animate-in"
        :class="`animate-in-delay-${Math.min(i + 1, 4)}`"
      >
        <h3>{{ project.name }}</h3>
        <div class="project-meta">
          <span class="status-badge" :class="project.status">{{ project.status }}</span>
        </div>
      </router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { api } from '@/api/client'

const projects = ref<any[]>([])
const loading = ref(true)
const error = ref('')
const showForm = ref(false)
const newName = ref('')

async function fetchProjects() {
  loading.value = true
  error.value = ''
  try {
    const data = await api.listProjects()
    projects.value = data.projects || []
  } catch (e: any) {
    error.value = e.message || 'Failed to load projects'
  } finally {
    loading.value = false
  }
}

async function createProject() {
  const name = newName.value.trim()
  if (!name) return
  try {
    await api.createProject(name)
    newName.value = ''
    showForm.value = false
    await fetchProjects()
  } catch (e: any) {
    error.value = e.message || 'Failed to create project'
  }
}

onMounted(fetchProjects)
</script>

<style scoped>
.project-list-page {
  max-width: 900px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 2rem;
}

.create-form {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 2rem;
  align-items: center;
}

.create-form input {
  flex: 1;
  max-width: 300px;
}

.project-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 1rem;
}

.project-card {
  text-decoration: none;
  display: block;
  cursor: pointer;
}

.project-card h3 {
  font-family: var(--font-display);
  margin-bottom: 0.75rem;
}

.project-meta {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.status-badge {
  font-size: 0.75rem;
  padding: 0.2rem 0.6rem;
  border-radius: 99px;
  background: var(--bg-hover);
  color: var(--text-muted);
  text-transform: capitalize;
}

.loading-state, .error-state, .empty-state {
  text-align: center;
  padding: 4rem 2rem;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.4;
}

.empty-state h3 {
  margin-bottom: 0.5rem;
}
</style>
