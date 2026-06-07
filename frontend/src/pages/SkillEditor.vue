<template>
  <div class="skills-page">
    <div class="page-header animate-in">
      <router-link :to="`/project/${projectId}`" class="back-link">← Project</router-link>
      <h1>Skills</h1>
    </div>

    <div class="skills-layout">
      <!-- Sidebar: skill tree -->
      <aside class="skills-sidebar card animate-in animate-in-delay-1">
        <div class="sidebar-header">
          <h3>Skill Tree</h3>
          <button class="btn btn-sm btn-ghost" @click="refreshSkills" :disabled="loading">⟳</button>
        </div>

        <div v-if="loading" class="loading-state"><p>Loading...</p></div>
        <div v-else-if="skillTree.length === 0" class="empty-subtle">
          <p>No skills found.</p>
        </div>
        <div v-else class="tree-list">
          <div v-for="cat in skillTree" :key="cat.name" class="tree-category">
            <div class="tree-category-header" @click="toggleCategory(cat.name)">
              <span class="tree-arrow" :class="{ expanded: expandedCategories.has(cat.name) }">▶</span>
              <span class="cat-name">{{ cat.name }}</span>
            </div>
            <div v-if="expandedCategories.has(cat.name)" class="tree-children">
              <div
                v-for="child in cat.children"
                :key="child.name"
                class="tree-skill"
                :class="{ selected: selectedSkill?.name === child.name }"
                @click="selectSkill(child.name)"
              >
                {{ child.name }}
                <span v-if="!child.is_active" class="inactive-tag">inactive</span>
              </div>
            </div>
          </div>
        </div>
      </aside>

      <!-- Main: detail panel -->
      <div class="skills-main animate-in animate-in-delay-2">
        <div v-if="!selectedSkill" class="empty-subtle">
          <p>Select a skill from the tree to edit.</p>
        </div>

        <template v-else>
          <!-- Tab bar -->
          <div class="tab-bar">
            <button
              v-for="tab in tabs"
              :key="tab.key"
              class="tab-btn"
              :class="{ active: activeTab === tab.key }"
              @click="activeTab = tab.key"
            >{{ tab.label }}</button>
          </div>

          <!-- === Edit Tab === -->
          <div v-if="activeTab === 'edit'" class="tab-panel">
            <div class="form-grid">
              <div class="form-field">
                <label>Name</label>
                <input :value="selectedSkill.name" disabled class="input-readonly" />
              </div>
              <div class="form-field">
                <label>Category</label>
                <input :value="selectedSkill.category" disabled class="input-readonly" />
              </div>
              <div class="form-field">
                <label>Model</label>
                <input v-model="editForm.model" />
              </div>
              <div class="form-field">
                <label>Temperature</label>
                <input v-model.number="editForm.temperature" type="number" step="0.1" min="0" max="2" />
              </div>
              <div class="form-field">
                <label>Max Tokens</label>
                <input v-model.number="editForm.max_tokens" type="number" min="256" />
              </div>
              <div class="form-field">
                <label>Fallback Model</label>
                <input v-model="editForm.fallback_model" placeholder="None" />
              </div>
            </div>

            <div class="form-field textarea-field">
              <label>Description</label>
              <textarea v-model="editForm.description" rows="2"></textarea>
            </div>

            <div class="form-field textarea-field">
              <label>System Prompt</label>
              <textarea v-model="editForm.system_prompt" rows="8" class="code-input"></textarea>
            </div>

            <div class="form-field textarea-field">
              <label>User Prompt Template (Jinja2)</label>
              <textarea v-model="editForm.user_prompt_template" rows="6" class="code-input"></textarea>
            </div>

            <div class="form-field textarea-field">
              <label>Post-Process Template</label>
              <textarea v-model="editForm.post_process_template" rows="3" class="code-input"></textarea>
            </div>

            <div class="form-actions">
              <button class="btn btn-primary" @click="saveSkill" :disabled="saving">
                {{ saving ? 'Saving...' : 'Save Changes' }}
              </button>
              <span v-if="saveMsg" class="save-msg" :class="saveMsgType">{{ saveMsg }}</span>
            </div>
          </div>

          <!-- === Versions Tab === -->
          <div v-if="activeTab === 'versions'" class="tab-panel">
            <div v-if="versionsLoading" class="loading-state"><p>Loading versions...</p></div>
            <div v-else-if="versions.length === 0" class="empty-subtle">
              <p>No version history yet.</p>
            </div>
            <div v-else class="version-list">
              <div
                v-for="v in versions"
                :key="v.version"
                class="version-item"
                :class="{ 'version-current': v.version === selectedSkill.version }"
              >
                <div class="version-header">
                  <span class="version-num">v{{ v.version }}</span>
                  <span v-if="v.version === selectedSkill.version" class="current-tag">current</span>
                  <span class="version-date">{{ v.created_at ? new Date(v.created_at).toLocaleDateString() : '' }}</span>
                </div>
                <div class="version-model">{{ v.model }}</div>
                <div class="version-note">{{ v.change_note || 'No change note' }}</div>
                <button
                  v-if="v.version !== selectedSkill.version"
                  class="btn btn-sm btn-ghost"
                  @click="rollback(v.version)"
                >Rollback to v{{ v.version }}</button>
              </div>
            </div>
          </div>

          <!-- === Execute Tab === -->
          <div v-if="activeTab === 'execute'" class="tab-panel">
            <div class="form-field">
              <label>Chapter Number</label>
              <input v-model.number="execForm.chapter_number" type="number" min="1" />
            </div>
            <div class="form-field textarea-field">
              <label>Chapter Content (optional)</label>
              <textarea v-model="execForm.chapter_content" rows="4" placeholder="Existing draft content..."></textarea>
            </div>
            <div class="form-field textarea-field">
              <label>Outline (optional)</label>
              <textarea v-model="execForm.current_outline" rows="3" placeholder="Current outline..."></textarea>
            </div>
            <div class="form-field textarea-field">
              <label>Instructions (optional)</label>
              <textarea v-model="execForm.supervisor_instructions" rows="2" placeholder="Specific guidance..."></textarea>
            </div>

            <button class="btn btn-primary" @click="executeSkill" :disabled="executing">
              {{ executing ? 'Running...' : '▶ Execute' }}
            </button>

            <div v-if="execResult" class="exec-result">
              <div class="exec-meta">
                <span>Model: {{ execResult.model_used }}</span>
                <span>Tokens: {{ execResult.tokens_in }}→{{ execResult.tokens_out }}</span>
                <span>Cost: ${{ execResult.cost_usd.toFixed(6) }}</span>
              </div>
              <pre class="exec-content">{{ execResult.content }}</pre>
            </div>

            <div v-if="execError" class="error-msg">{{ execError }}</div>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '@/api/client'

const route = useRoute()
const projectId = route.params.id as string

// ── Data ──
const loading = ref(true)
const skillTree = ref<any[]>([])
const skillMap = ref<Record<string, any>>({})
const selectedSkill = ref<any>(null)
const expandedCategories = ref<Set<string>>(new Set())

const tabs = [
  { key: 'edit', label: 'Edit' },
  { key: 'versions', label: 'Versions' },
  { key: 'execute', label: 'Execute' },
]
const activeTab = ref('edit')

// Edit form
const editForm = reactive({
  description: '',
  system_prompt: '',
  user_prompt_template: '',
  post_process_template: '',
  model: '',
  fallback_model: '',
  max_tokens: 4096,
  temperature: 0.7,
})
const saving = ref(false)
const saveMsg = ref('')
const saveMsgType = ref<'success' | 'error'>('success')

// Versions
const versions = ref<any[]>([])
const versionsLoading = ref(false)

// Execute
const execForm = reactive({
  chapter_number: 1,
  chapter_content: '',
  current_outline: '',
  supervisor_instructions: '',
})
const executing = ref(false)
const execResult = ref<any>(null)
const execError = ref('')

// ── Methods ──
async function refreshSkills() {
  loading.value = true
  try {
    const data = await api.listSkills()
    skillTree.value = data.tree || []
    // Build name→skill lookup
    const map: Record<string, any> = {}
    function walk(items: any[]) {
      for (const item of items) {
        map[item.name] = item
        if (item.children) walk(item.children)
      }
    }
    walk(data.tree || [])
    skillMap.value = map

    // Expand all categories by default
    for (const cat of data.tree || []) {
      expandedCategories.value.add(cat.name)
    }
  } catch (e) {
    console.error('Failed to load skills', e)
  } finally {
    loading.value = false
  }
}

async function selectSkill(name: string) {
  try {
    const skill = await api.getSkill(name)
    selectedSkill.value = skill
    Object.assign(editForm, {
      description: skill.description || '',
      system_prompt: skill.system_prompt || '',
      user_prompt_template: skill.user_prompt_template || '',
      post_process_template: skill.post_process_template || '',
      model: skill.model || '',
      fallback_model: skill.fallback_model || '',
      max_tokens: skill.max_tokens || 4096,
      temperature: skill.temperature ?? 0.7,
    })
    activeTab.value = 'edit'
    execResult.value = null
    execError.value = ''
  } catch (e) {
    console.error('Failed to load skill detail', e)
  }
}

function toggleCategory(name: string) {
  if (expandedCategories.value.has(name)) {
    expandedCategories.value.delete(name)
  } else {
    expandedCategories.value.add(name)
  }
}

async function saveSkill() {
  saving.value = true
  saveMsg.value = ''
  try {
    const updated = await api.updateSkill(selectedSkill.value!.name, editForm)
    // Update local cache
    selectedSkill.value = { ...selectedSkill.value, ...editForm }
    saveMsg.value = 'Saved successfully'
    saveMsgType.value = 'success'
    setTimeout(() => (saveMsg.value = ''), 3000)
  } catch (e: any) {
    saveMsg.value = e.message || 'Save failed'
    saveMsgType.value = 'error'
  } finally {
    saving.value = false
  }
}

async function loadVersions() {
  if (!selectedSkill.value) return
  versionsLoading.value = true
  try {
    const data = await api.getSkillVersions(selectedSkill.value.name)
    versions.value = data.versions || []
  } catch (e) {
    console.error('Failed to load versions', e)
  } finally {
    versionsLoading.value = false
  }
}

async function rollback(version: number) {
  if (!selectedSkill.value) return
  try {
    const updated = await api.rollbackSkill(selectedSkill.value.name, version)
    selectedSkill.value = updated
    Object.assign(editForm, {
      description: updated.description || '',
      system_prompt: updated.system_prompt || '',
      user_prompt_template: updated.user_prompt_template || '',
      post_process_template: updated.post_process_template || '',
      model: updated.model || '',
      fallback_model: updated.fallback_model || '',
      max_tokens: updated.max_tokens || 4096,
      temperature: updated.temperature ?? 0.7,
    })
    await loadVersions()
  } catch (e) {
    console.error('Rollback failed', e)
  }
}

async function executeSkill() {
  executing.value = true
  execResult.value = null
  execError.value = ''
  try {
    const result = await api.executeSkill(selectedSkill.value!.name, {
      project_id: projectId,
      chapter_number: execForm.chapter_number,
      chapter_content: execForm.chapter_content || null,
      current_outline: execForm.current_outline || null,
      supervisor_instructions: execForm.supervisor_instructions || null,
    })
    execResult.value = result
  } catch (e: any) {
    execError.value = e.message || 'Execution failed'
  } finally {
    executing.value = false
  }
}

// Switch to versions tab → load versions
watch(activeTab, (tab) => {
  if (tab === 'versions') loadVersions()
})

onMounted(refreshSkills)
</script>

<style scoped>
.skills-page {
  max-width: 1200px;
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

/* Layout */
.skills-layout {
  display: grid;
  grid-template-columns: 260px 1fr;
  gap: 1.5rem;
  min-height: 70vh;
}

@media (max-width: 800px) {
  .skills-layout { grid-template-columns: 1fr; }
}

/* Sidebar */
.skills-sidebar {
  padding: 1rem;
  max-height: calc(100vh - 140px);
  overflow-y: auto;
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.sidebar-header h3 {
  font-family: var(--font-display);
  font-size: 1rem;
}

.tree-list {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.tree-category-header {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.4rem 0.5rem;
  cursor: pointer;
  border-radius: 4px;
  font-weight: 500;
  font-size: 0.9rem;
  transition: background 0.15s;
}

.tree-category-header:hover {
  background: var(--bg-hover);
}

.tree-arrow {
  font-size: 0.6rem;
  transition: transform 0.15s;
  color: var(--text-muted);
}

.tree-arrow.expanded {
  transform: rotate(90deg);
}

.tree-children {
  margin-left: 1.2rem;
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.tree-skill {
  padding: 0.35rem 0.5rem 0.35rem 1rem;
  cursor: pointer;
  border-radius: 4px;
  font-size: 0.85rem;
  color: var(--text-secondary);
  transition: all 0.15s;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.tree-skill:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.tree-skill.selected {
  background: var(--accent);
  color: var(--btn-primary-text);
  font-weight: 500;
}

.inactive-tag {
  font-size: 0.65rem;
  padding: 0.1rem 0.3rem;
  border-radius: 4px;
  background: rgba(224, 107, 107, 0.15);
  color: var(--error);
}

/* Main panel */
.skills-main {
  min-height: 400px;
}

/* Tabs */
.tab-bar {
  display: flex;
  gap: 2px;
  border-bottom: 1px solid var(--border);
  margin-bottom: 1.5rem;
}

.tab-btn {
  padding: 0.6rem 1.2rem;
  background: transparent;
  color: var(--text-muted);
  font-size: 0.85rem;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
}

.tab-btn:hover {
  color: var(--text-secondary);
}

.tab-btn.active {
  color: var(--accent);
  border-bottom-color: var(--accent);
}

.tab-panel {
  min-height: 300px;
}

/* Form */
.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1rem;
}

@media (max-width: 600px) {
  .form-grid { grid-template-columns: 1fr; }
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.form-field label {
  font-size: 0.75rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.form-field input,
.form-field textarea {
  width: 100%;
}

.input-readonly {
  opacity: 0.6;
  cursor: not-allowed;
}

.textarea-field {
  grid-column: 1 / -1;
}

.code-input {
  font-family: 'SF Mono', 'Menlo', monospace;
  font-size: 0.8rem;
  line-height: 1.5;
}

.form-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-top: 1.5rem;
}

.save-msg {
  font-size: 0.85rem;
  padding: 0.3rem 0.8rem;
  border-radius: 4px;
}

.save-msg.success {
  color: var(--success);
  background: rgba(107, 207, 127, 0.1);
}

.save-msg.error {
  color: var(--error);
  background: rgba(224, 107, 107, 0.1);
}

/* Versions */
.version-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.version-item {
  padding: 0.75rem 1rem;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 6px;
  display: flex;
  align-items: center;
  gap: 1rem;
  font-size: 0.85rem;
}

.version-current {
  border-color: var(--accent);
  background: var(--bg-hover);
}

.version-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  min-width: 100px;
}

.version-num {
  font-weight: 600;
  font-family: 'SF Mono', 'Menlo', monospace;
}

.current-tag {
  font-size: 0.65rem;
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
  background: var(--accent);
  color: var(--btn-primary-text);
}

.version-date {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.version-model {
  color: var(--text-secondary);
  min-width: 200px;
  font-family: 'SF Mono', 'Menlo', monospace;
  font-size: 0.8rem;
}

.version-note {
  flex: 1;
  color: var(--text-muted);
  font-style: italic;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Execute */
.exec-result {
  margin-top: 1.5rem;
  padding: 1rem;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 6px;
}

.exec-meta {
  display: flex;
  gap: 1.5rem;
  font-size: 0.8rem;
  color: var(--text-muted);
  margin-bottom: 1rem;
  font-family: 'SF Mono', 'Menlo', monospace;
}

.exec-content {
  font-size: 0.85rem;
  line-height: 1.6;
  white-space: pre-wrap;
  word-wrap: break-word;
  max-height: 500px;
  overflow-y: auto;
  color: var(--text-primary);
}

.error-msg {
  margin-top: 1rem;
  color: var(--error);
  font-size: 0.85rem;
}

.loading-state, .empty-subtle {
  text-align: center;
  padding: 3rem 1rem;
  color: var(--text-muted);
}
</style>
