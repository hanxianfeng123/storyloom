const BASE = '/api'

export interface Project {
  id: string
  name: string
  status: string
}

export interface Chapter {
  number: number
  title: string
  status: string
  word_count: number
  summary: string
}

export interface Character {
  name: string
  role: string
  status: string
  location: string
}

export interface PlotThread {
  name: string
  status: string
  first_chapter: number
  description: string
}

export interface PipelineStatus {
  pipeline_id: string
  status: string
  stage_results?: { stage: string; decision: string }[]
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    const err = await res.text()
    throw new Error(`API error ${res.status}: ${err}`)
  }
  return res.json()
}

export const api = {
  // Projects
  listProjects: () => request<{ projects: Project[] }>('/projects/'),
  createProject: (name: string) => request<{ name: string; status: string }>(`/projects/?name=${encodeURIComponent(name)}`, { method: 'POST' }),

  // Pipeline
  startPipeline: (projectId: string, chapter: number) =>
    request<PipelineStatus>(`/pipeline/start?project_id=${encodeURIComponent(projectId)}&chapter=${chapter}`, { method: 'POST' }),
  getPipelineStatus: (pipelineId: string) =>
    request<PipelineStatus>(`/pipeline/status/${encodeURIComponent(pipelineId)}`),
  cancelPipeline: (pipelineId: string) =>
    request<{ status: string }>(`/pipeline/cancel/${encodeURIComponent(pipelineId)}`, { method: 'POST' }),

  // Memory
  listCharacters: (projectId: string) =>
    request<{ characters: Character[] }>(`/memory/characters/${encodeURIComponent(projectId)}`),
  listPlotThreads: (projectId: string) =>
    request<{ plot_threads: PlotThread[] }>(`/memory/plot-threads/${encodeURIComponent(projectId)}`),

  // Chapters
  listChapters: (projectId: string) =>
    request<{ chapters: Chapter[] }>(`/chapters/${encodeURIComponent(projectId)}`),
  getChapter: (projectId: string, number: number) =>
    request<{ chapter: Chapter | null }>(`/chapters/${encodeURIComponent(projectId)}/${number}`),

  // Skills
  listSkills: () => request<{ tree: any[]; active: any[] }>('/skills/'),
  getSkill: (name: string) => request<any>(`/skills/${encodeURIComponent(name)}`),
  updateSkill: (name: string, data: any) =>
    request<any>(`/skills/${encodeURIComponent(name)}`, { method: 'PUT', body: JSON.stringify(data) }),
  getSkillVersions: (name: string) =>
    request<{ versions: any[] }>(`/skills/${encodeURIComponent(name)}/versions`),
  rollbackSkill: (name: string, targetVersion: number) =>
    request<any>(`/skills/${encodeURIComponent(name)}/rollback?target_version=${targetVersion}`, { method: 'POST' }),
  executeSkill: (name: string, data: any) =>
    request<any>(`/skills/${encodeURIComponent(name)}/execute`, { method: 'POST', body: JSON.stringify(data) }),
}
