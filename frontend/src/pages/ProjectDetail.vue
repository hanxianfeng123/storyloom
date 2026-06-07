<template>
  <div class="project-detail-page">
    <div class="page-header animate-in">
      <router-link to="/" class="back-link">← Back</router-link>
      <h1>{{ projectId }}</h1>
    </div>

    <div class="action-bar animate-in animate-in-delay-1">
      <router-link :to="`/project/${projectId}/pipeline`" class="btn btn-primary">
        ▶ Run Pipeline
      </router-link>
      <router-link :to="`/project/${projectId}/memory`" class="btn btn-ghost">
        Memory Explorer
      </router-link>
      <router-link :to="`/project/${projectId}/skills`" class="btn btn-ghost">
        Skills
      </router-link>
    </div>

    <section class="section animate-in animate-in-delay-2">
      <h2>Chapters</h2>

      <div v-if="loading" class="loading-state"><p>Loading chapters...</p></div>
      <div v-else-if="chapters.length === 0" class="empty-subtle">
        <p>No chapters yet. Run the pipeline to generate your first chapter.</p>
      </div>
      <div v-else class="chapter-list">
        <div
          v-for="(ch, i) in chapters"
          :key="ch.number"
          class="chapter-item animate-in"
          :class="`animate-in-delay-${Math.min(i + 1, 4)}`"
        >
          <div class="chapter-number">Ch {{ ch.number }}</div>
          <div class="chapter-info">
            <div class="chapter-title">{{ ch.title || 'Untitled' }}</div>
            <div class="chapter-meta">
              <span class="status-badge" :class="ch.status">{{ ch.status }}</span>
              <span class="word-count">{{ ch.word_count }} words</span>
            </div>
          </div>
          <div class="chapter-summary">{{ ch.summary || 'No summary' }}</div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '@/api/client'

const route = useRoute()
const projectId = route.params.id as string
const chapters = ref<any[]>([])
const loading = ref(true)

onMounted(async () => {
  try {
    const data = await api.listChapters(projectId)
    chapters.value = data.chapters || []
  } catch (e) {
    console.error('Failed to load chapters', e)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.project-detail-page {
  max-width: 800px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.back-link {
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.action-bar {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 3rem;
}

.section {
  margin-bottom: 2rem;
}

.section h2 {
  font-family: var(--font-display);
  margin-bottom: 1.25rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--border);
}

.chapter-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.chapter-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.25rem;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  transition: all 0.2s;
}

.chapter-item:hover {
  border-color: var(--border-light);
}

.chapter-number {
  font-family: var(--font-display);
  font-size: 1.1rem;
  color: var(--accent);
  min-width: 60px;
}

.chapter-info {
  flex: 1;
}

.chapter-title {
  font-weight: 500;
  margin-bottom: 0.25rem;
}

.chapter-meta {
  display: flex;
  gap: 0.75rem;
  font-size: 0.8rem;
  color: var(--text-muted);
}

.status-badge {
  font-size: 0.7rem;
  padding: 0.15rem 0.5rem;
  border-radius: 99px;
  background: var(--bg-hover);
  color: var(--text-muted);
  text-transform: capitalize;
}

.chapter-summary {
  font-size: 0.85rem;
  color: var(--text-secondary);
  max-width: 250px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.loading-state, .empty-subtle {
  text-align: center;
  padding: 3rem 1rem;
  color: var(--text-muted);
}
</style>
