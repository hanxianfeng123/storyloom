<template>
  <div class="pipeline-page">
    <div class="page-header animate-in">
      <router-link :to="`/project/${projectId}`" class="back-link">← Project</router-link>
      <h1>Pipeline</h1>
    </div>

    <div class="pipeline-controls animate-in animate-in-delay-1">
      <div class="chapter-input">
        <label>Chapter</label>
        <input v-model.number="chapterNumber" type="number" min="1" placeholder="1" />
      </div>
      <button
        class="btn btn-primary"
        @click="startPipeline"
        :disabled="running"
      >
        {{ running ? 'Running...' : '▶ Start Pipeline' }}
      </button>
      <button
        class="btn btn-danger"
        @click="cancelPipeline"
        :disabled="!running"
      >
        ✕ Cancel
      </button>
    </div>

    <div class="pipeline-visual animate-in animate-in-delay-2">
      <div
        v-for="(stage, i) in stages"
        :key="stage.name"
        class="stage-node"
        :class="{
          'stage-active': stage.status === 'running',
          'stage-pass': stage.status === 'approved',
          'stage-fail': stage.status === 'failed',
          'stage-skip': stage.status === 'skipped',
        }"
      >
        <div class="stage-indicator">
          <span v-if="stage.status === 'running'" class="spinner"></span>
          <span v-else-if="stage.status === 'approved'">✓</span>
          <span v-else-if="stage.status === 'failed'">✕</span>
          <span v-else>{{ i + 1 }}</span>
        </div>
        <div class="stage-label">{{ stage.label }}</div>
        <div class="stage-status">{{ stage.status }}</div>
      </div>
    </div>

    <div v-if="pipelineId" class="pipeline-id animate-in animate-in-delay-3">
      Pipeline: <code>{{ pipelineId }}</code>
    </div>

    <div v-if="error" class="error-msg">{{ error }}</div>

    <div class="stage-output animate-in animate-in-delay-3" v-if="results.length > 0">
      <h3>Results</h3>
      <div v-for="r in results" :key="r.stage" class="result-item">
        <span class="result-stage">{{ r.stage }}</span>
        <span class="result-decision" :class="r.decision">{{ r.decision }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '@/api/client'

const route = useRoute()
const projectId = route.params.id as string
const chapterNumber = ref(1)
const running = ref(false)
const pipelineId = ref('')
const error = ref('')
const results = ref<{ stage: string; decision: string }[]>([])
let ws: WebSocket | null = null

const stages = ref([
  { name: 'planner', label: 'Planner', status: 'idle' },
  { name: 'writer', label: 'Writer', status: 'idle' },
  { name: 'editor', label: 'Editor', status: 'idle' },
  { name: 'continuity', label: 'Continuity', status: 'idle' },
  { name: 'quality_gate', label: 'Quality Gate', status: 'idle' },
])

async function startPipeline() {
  running.value = true
  error.value = ''
  results.value = []
  stages.value.forEach(s => (s.status = 'idle'))

  try {
    const data = await api.startPipeline(projectId, chapterNumber.value)
    pipelineId.value = data.pipeline_id

    // Connect WebSocket for progress
    connectWs(data.pipeline_id)

    // Poll for status
    pollStatus(data.pipeline_id)
  } catch (e: any) {
    error.value = e.message || 'Failed to start pipeline'
    running.value = false
  }
}

function connectWs(pid: string) {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  ws = new WebSocket(`${protocol}//${window.location.host}/ws/pipeline/${pid}`)
  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      if (data.stage) {
        const s = stages.value.find(st => st.name === data.stage)
        if (s) s.status = data.stage_status || 'running'
      }
    } catch {}
  }
}

let pollTimer: ReturnType<typeof setInterval> | null = null

function pollStatus(pid: string) {
  pollTimer = setInterval(async () => {
    try {
      const data = await api.getPipelineStatus(pid)
      if (data.stage_results) {
        results.value = data.stage_results
        data.stage_results.forEach(r => {
          const s = stages.value.find(st => st.name === r.stage)
          if (s) s.status = r.decision
        })
      }
      if (data.status === 'completed' || data.status === 'failed' || data.status === 'cancelled') {
        running.value = false
        if (pollTimer) clearInterval(pollTimer)
        if (ws) ws.close()
      }
    } catch {
      running.value = false
      if (pollTimer) clearInterval(pollTimer)
    }
  }, 1000)
}

async function cancelPipeline() {
  if (!pipelineId.value) return
  try {
    await api.cancelPipeline(pipelineId.value)
    running.value = false
    if (pollTimer) clearInterval(pollTimer)
    if (ws) ws.close()
    error.value = 'Pipeline cancelled'
  } catch (e: any) {
    error.value = e.message || 'Failed to cancel'
  }
}

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
  if (ws) ws.close()
})
</script>

<style scoped>
.pipeline-page {
  max-width: 800px;
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

.pipeline-controls {
  display: flex;
  gap: 0.75rem;
  align-items: flex-end;
  margin-bottom: 3rem;
}

.chapter-input {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.chapter-input label {
  font-size: 0.8rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.chapter-input input {
  width: 80px;
  text-align: center;
}

.pipeline-visual {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  margin-bottom: 2rem;
  padding: 2rem;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
}

.stage-node {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  position: relative;
}

.stage-node + .stage-node::before {
  content: '';
  position: absolute;
  left: -0.5rem;
  top: 30%;
  width: 0.5rem;
  height: 2px;
  background: var(--border);
}

.stage-indicator {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.9rem;
  font-weight: 600;
  background: var(--bg-hover);
  border: 2px solid var(--border);
  color: var(--text-muted);
  transition: all 0.3s;
}

.stage-active .stage-indicator {
  border-color: var(--accent);
  color: var(--accent);
  animation: glowPulse 1.5s ease infinite;
}

.stage-pass .stage-indicator {
  border-color: var(--success);
  color: var(--success);
  background: rgba(107, 207, 127, 0.1);
}

.stage-fail .stage-indicator {
  border-color: var(--error);
  color: var(--error);
  background: rgba(224, 107, 107, 0.1);
}

.stage-label {
  font-size: 0.8rem;
  font-weight: 500;
  color: var(--text-secondary);
}

.stage-status {
  font-size: 0.7rem;
  color: var(--text-muted);
  text-transform: capitalize;
}

.spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid var(--accent);
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.pipeline-id {
  text-align: center;
  margin-bottom: 1rem;
  font-size: 0.85rem;
  color: var(--text-muted);
}

.pipeline-id code {
  color: var(--accent);
  font-size: 0.8rem;
}

.error-msg {
  text-align: center;
  color: var(--error);
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

.stage-output {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1.5rem;
}

.stage-output h3 {
  font-family: var(--font-display);
  margin-bottom: 1rem;
}

.result-item {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
  border-bottom: 1px solid var(--border);
  font-size: 0.9rem;
}

.result-item:last-child { border-bottom: none; }

.result-decision {
  font-size: 0.8rem;
  padding: 0.15rem 0.5rem;
  border-radius: 99px;
  text-transform: capitalize;
}

.result-decision.approved { background: rgba(107, 207, 127, 0.15); color: var(--success); }
.result-decision.failed { background: rgba(224, 107, 107, 0.15); color: var(--error); }
.result-decision.forced_pass { background: rgba(232, 184, 75, 0.15); color: var(--warning); }
</style>
