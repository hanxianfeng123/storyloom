<template>
  <div class="theme-toggle">
    <button
      v-for="t in themes"
      :key="t.id"
      class="theme-btn"
      :class="{ active: current === t.id }"
      :title="t.label"
      @click="setTheme(t.id)"
    >
      <span class="theme-swatch" :style="{ background: t.color }"></span>
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const themes = [
  { id: 'manuscript', label: 'Manuscript — warm light', color: '#faf6f0' },
  { id: 'sepia', label: 'Sepia — warm medium', color: '#f0e6d3' },
  { id: 'dark', label: 'Dark — night mode', color: '#1a1a2e' },
]

const current = ref('manuscript')

function setTheme(id: string) {
  current.value = id
  document.documentElement.className = `theme-${id}`
  localStorage.setItem('storyloom-theme', id)
}

onMounted(() => {
  const saved = localStorage.getItem('storyloom-theme') || 'manuscript'
  setTheme(saved)
})
</script>

<style scoped>
.theme-toggle {
  display: flex;
  gap: 0.4rem;
  align-items: center;
}

.theme-btn {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: 2px solid var(--border);
  padding: 0;
  cursor: pointer;
  transition: all 0.2s ease;
}

.theme-btn:hover {
  border-color: var(--accent);
  transform: scale(1.1);
}

.theme-btn.active {
  border-color: var(--accent);
  box-shadow: 0 0 12px rgba(201, 149, 107, 0.3);
}

.theme-swatch {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  display: block;
  border: 1px solid rgba(0, 0, 0, 0.1);
}
</style>
