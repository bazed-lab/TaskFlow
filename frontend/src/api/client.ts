const BASE = '/api'

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = localStorage.getItem('access_token')
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  }
  if (token) headers['Authorization'] = `Bearer ${token}`

  const res = await fetch(`${BASE}${path}`, { ...options, headers })

  if (res.status === 401) {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    window.location.hash = '#login'
    throw new Error('Unauthorized')
  }

  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    const detail = body.detail
    const msg = Array.isArray(detail)
      ? detail.map((e: any) => e.msg).join('; ')
      : typeof detail === 'string'
        ? detail
        : `Error ${res.status}`
    throw new Error(msg)
  }

  return res.json()
}

export const api = {
  // Auth
  signup: (data: { email: string; password: string; username: string; handle: string }) =>
    request<{ message: string }>('/auth/signup', { method: 'POST', body: JSON.stringify(data) }),

  login: (data: { email: string; password: string }) =>
    request<{ access_token: string; refresh_token: string }>('/auth/login', { method: 'POST', body: JSON.stringify(data) }),

  refresh: () =>
    request<{ access_token: string; refresh_token: string }>('/auth/refresh', { method: 'POST' }),

  logout: (refresh_token: string) =>
    request<{ message: string }>('/auth/logout', {
      method: 'POST',
      body: JSON.stringify({ refresh_token }),
    }),

  // Users
  getMe: () => request<{ id: number; email: string; username: string; handle: string; is_active: boolean; is_superuser: boolean }>('/users/me'),

  updateMe: (data: Record<string, unknown>) =>
    request<{ id: number; email: string; username: string; handle: string; is_active: boolean; is_superuser: boolean }>('/users/me', {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),

  // Projects
  createProject: (data: { name: string; description?: string | null; secret_key?: string | null }) =>
    request<{ id: string; name: string; description: string | null; secret_key: string | null; owner_id: number; is_active: boolean; created_at: string }>(
      '/projects',
      { method: 'POST', body: JSON.stringify(data) },
    ),

  getProjects: () =>
    request<Array<{ id: string; name: string; description: string | null; secret_key: string | null; owner_id: number; is_active: boolean; created_at: string }>>(
      '/projects',
    ),

  getProject: (projectId: string) =>
    request<{
      project: { id: string; name: string; description: string | null; secret_key: string | null; owner_id: number; is_active: boolean; created_at: string }
      members: Array<{ id: number; user_id: number; role: string; username: string; handle: string }>
    }>(`/projects/${projectId}`),

  addMember: (projectId: string, data: { handle: string; role?: string }) =>
    request<{ id: number; user_id: number; role: string; username: string; handle: string }>(`/projects/${projectId}/members`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  updateMemberRole: (projectId: string, userId: number, data: { role: string }) =>
    request<{ id: number; user_id: number; role: string }>(`/projects/${projectId}/members/${userId}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),

  removeMember: (projectId: string, userId: number) =>
    request<{ message: string }>(`/projects/${projectId}/members/${userId}`, { method: 'DELETE' }),

  joinProject: (invite: string) =>
    request<{ id: number; user_id: number; role: string }>('/projects/join', {
      method: 'POST',
      body: JSON.stringify({ invite }),
    }),

  // Tasks
  createTask: (projectId: string, data: { title: string; description?: string | null; assigned_to?: number | null; priority?: string; deadline?: string | null }) =>
    request<{ id: number; project_id: string; title: string; description: string | null; assigned_to: number | null; created_by: number; status: string; priority: string; deadline: string | null; completed_by: number | null; completed_at: string | null; completion_comment: string | null; created_at: string; updated_at: string | null }>(
      `/projects/${projectId}/tasks`,
      { method: 'POST', body: JSON.stringify(data) },
    ),

  getTasks: (projectId: string) =>
    request<Array<{ id: number; project_id: string; title: string; description: string | null; assigned_to: number | null; created_by: number; status: string; priority: string; deadline: string | null; completed_by: number | null; completed_at: string | null; completion_comment: string | null; created_at: string; updated_at: string | null }>>(
      `/projects/${projectId}/tasks`,
    ),

  updateTask: (projectId: string, taskId: number, data: { title?: string; description?: string | null; assigned_to?: number | null; status?: string; priority?: string }) =>
    request<{ id: number; project_id: string; title: string; description: string | null; assigned_to: number | null; created_by: number; status: string; priority: string; deadline: string | null; completed_by: number | null; completed_at: string | null; completion_comment: string | null; created_at: string; updated_at: string | null }>(
      `/projects/${projectId}/tasks/${taskId}`,
      { method: 'PATCH', body: JSON.stringify(data) },
    ),

  completeTask: (projectId: string, taskId: number, comment?: string | null) =>
    request<{ id: number; project_id: string; title: string; description: string | null; assigned_to: number | null; created_by: number; status: string; priority: string; deadline: string | null; completed_by: number; completed_at: string; completion_comment: string | null; created_at: string; updated_at: string | null }>(
      `/projects/${projectId}/tasks/${taskId}/complete`,
      { method: 'PATCH', body: JSON.stringify({ comment: comment || null }) },
    ),

  getCompletedTasks: (projectId: string) =>
    request<Array<{ id: number; project_id: string; title: string; description: string | null; assigned_to: number | null; created_by: number; priority: string; deadline: string | null; completed_by: number; completed_by_username: string; completed_by_handle: string; completed_at: string; completion_comment: string | null; created_at: string }>>(
      `/projects/${projectId}/tasks/completed`,
    ),

  deleteTask: (projectId: string, taskId: number) =>
    request<{ message: string }>(`/projects/${projectId}/tasks/${taskId}`, { method: 'DELETE' }),
}
