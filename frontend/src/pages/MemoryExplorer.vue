<template>
  <div class="memory-page">
    <div class="page-header animate-in">
      <router-link :to="`/project/${projectId}`" class="back-link">← Project</router-link>
      <h1>Memory Explorer</h1>
    </div>

    <div class="memory-grid">
      <section class="section card animate-in animate-in-delay-1">
        <h2>Characters</h2>
        <div v-if="charsLoading" class="loading-state"><p>Loading...</p></div>
        <div v-else-if="characters.length === 0" class="empty-subtle">
          <p>No characters yet.</p>
        </div>
        <div v-else class="char-list">
          <div v-for="c in characters" :key="c.name" class="char-item">
            <div class="char-name">{{ c.name }}</div>
            <div class="char-detail">
              <span class="char-tag">{{ c.role }}</span>
              <span class="char-location">{{ c.location || 'unknown location' }}</span>
            </div>
            <span class="status-dot" :class="c.status"></span>
          </div>
        </div>
      </section>

      <section class="section card animate-in animate-in-delay-2">
        <h2>Plot Threads</h2>
        <div v-if="threadsLoading" class="loading-state"><p>Loading...</p></div>
        <div v-else-if="plotThreads.length === 0" class="empty-subtle">
          <p>No plot threads yet.</p>
        </div>
        <div v-else class="thread-list">
          <div v-for="t in plotThreads" :key="t.name" class="thread-item">
            <div class="thread-name">{{ t.name }}</div>
            <div class="thread-meta">
              <span class="status-badge" :class="t.status">{{ t.status }}</span>
              <span>Ch {{ t.first_chapter }}</span>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '@/api/client'

const route = useRoute()
const projectId = route.params.id as string

const characters = ref<any[]>([])
const charsLoading = ref(true)
const plotThreads = ref<any[]>([])
const threadsLoading = ref(true)

onMounted(async () => {
  try {
    const [charData, threadData] = await Promise.all([
      api.listCharacters(projectId),
      api.listPlotThreads(projectId),
    ])
    characters.value = charData.characters || []
    plotThreads.value = threadData.plot_threads || []
  } catch (e) {
    console.error('Failed to load memory data', e)
  } finally {
    charsLoading.value = false
    threadsLoading.value = false
  }
})
</script>

<style scoped>
.memory-page {
  max-width: 900px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.back-link {
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.memory-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

@media (max-width: 700px) {
  .memory-grid { grid-template-columns: 1fr; }
}

.section h2 {
  font-family: var(--font-display);
  margin-bottom: 1.25rem;
}

.char-list, .thread-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.char-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem;
  background: var(--bg-primary);
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
}

.char-name {
  font-weight: 500;
  min-width: 100px;
}

.char-detail {
  flex: 1;
  display: flex;
  gap: 0.75rem;
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.char-tag {
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
  background: var(--bg-hover);
  font-size: 0.75rem;
}

.char-location {
  color: var(--text-muted);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--text-muted);
}

.status-dot.active { background: var(--success); }
.status-dot.absent { background: var(--warning); }
.status-dot.deceased { background: var(--error); }

.thread-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem;
  background: var(--bg-primary);
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
}

.thread-name {
  font-weight: 500;
}

.thread-meta {
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

.status-badge.active { color: var(--success); }
.status-badge.resolved { color: var(--text-muted); }
.status-badge.abandoned { color: var(--error); }

.loading-state, .empty-subtle {
  text-align: center;
  padding: 2rem 1rem;
  color: var(--text-muted);
}
</style>
