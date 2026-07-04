import { useEffect, useState } from 'react'
import { api } from '../api/client'

type Task = {
  id: number
  project_id: string
  title: string
  description: string | null
  assigned_to: number | null
  created_by: number
  status: string
  priority: string
  deadline: string | null
  completed_by: number | null
  completed_at: string | null
  completion_comment: string | null
  created_at: string
  updated_at: string | null
}

type Member = {
  id: number
  user_id: number
  role: string
  username: string
  handle: string
}

type Props = {
  projectId: string
  isAdmin: boolean
  members: Member[]
  currentUserId: number
}

const STATUS_LABELS: Record<string, string> = {
  todo: 'Нужно сделать',
  in_progress: 'В работе',
  done: 'Готово',
}

const PRIORITY_LABELS: Record<string, string> = {
  low: 'Низкий',
  medium: 'Средний',
  high: 'Высокий',
}

const STATUS_OPTIONS = ['todo', 'in_progress', 'done']
const PRIORITY_OPTIONS = ['low', 'medium', 'high']

export default function TaskList({ projectId, isAdmin, members, currentUserId }: Props) {
  const [tasks, setTasks] = useState<Task[]>([])
  const [loading, setLoading] = useState(true)
  const [showCreate, setShowCreate] = useState(false)
  const [completeTask, setCompleteTask] = useState<Task | null>(null)
  const [error, setError] = useState('')

  const load = async () => {
    setLoading(true)
    try {
      const data = await api.getTasks(projectId)
      setTasks(data)
    } catch {}
    setLoading(false)
  }

  useEffect(() => { load() }, [projectId])

  const getMemberName = (userId: number | null) => {
    if (!userId) return null
    return members.find((m) => m.user_id === userId)?.username || null
  }

  const handleStatusChange = async (taskId: number, newStatus: string) => {
    try {
      await api.updateTask(projectId, taskId, { status: newStatus })
      load()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update status')
    }
  }

  const handleComplete = async (taskId: number, comment: string) => {
    try {
      await api.completeTask(projectId, taskId, comment || null)
      setCompleteTask(null)
      load()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to complete task')
    }
  }

  const handleDelete = async (taskId: number) => {
    if (!confirm('Удалить задачу?')) return
    try {
      await api.deleteTask(projectId, taskId)
      load()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete task')
    }
  }

  const isOverdue = (deadline: string | null) => {
    if (!deadline) return false
    return new Date(deadline) < new Date()
  }

  const formatDate = (d: string | null) => {
    if (!d) return ''
    return new Date(d).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' })
  }

  return (
    <div className="tasks-center">
      <div className="section-header" style={{ marginBottom: 20 }}>
        <h2>Задачи ({tasks.length})</h2>
        {isAdmin && (
          <button className="btn btn-primary btn-sm" onClick={() => setShowCreate(true)}>
            + Создать
          </button>
        )}
      </div>

      {error && <div className="form-error" style={{ marginBottom: 16 }}>{error}</div>}

      {loading ? (
        <div style={{ textAlign: 'center', padding: 48 }}><div className="spinner" /></div>
      ) : tasks.length === 0 ? (
        <div className="empty-state" style={{ padding: '48px 24px', background: 'var(--surface)', borderRadius: 'var(--radius)', border: '1px solid var(--border)' }}>
          <p>В проекте пока нет задач</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {tasks.map((task) => {
            const assigneeName = getMemberName(task.assigned_to)
            const isAssignee = task.assigned_to === currentUserId
            const isDone = task.status === 'done'
            const canComplete = (task.assigned_to === null || isAssignee) && !isDone
            return (
              <div key={task.id} className="task-card">
                <div className="task-card-header">
                  <span className="task-card-title">{task.title}</span>
                  <div className="task-card-badges">
                    <span className={`task-priority task-priority-${task.priority}`}>
                      {PRIORITY_LABELS[task.priority]}
                    </span>
                    {task.deadline && (
                      <span className={`deadline-badge ${isOverdue(task.deadline) && !isDone ? 'deadline-warning' : 'deadline-ok'}`}>
                        {isOverdue(task.deadline) && !isDone ? '⚠' : ''} {formatDate(task.deadline)}
                      </span>
                    )}
                  </div>
                </div>

                {task.description && (
                  <div className="task-card-desc">{task.description}</div>
                )}

                <div className="task-card-meta">
                  <span>
                    Статус:
                    <select
                      value={task.status}
                      onChange={(e) => handleStatusChange(task.id, e.target.value)}
                      className="task-status-select"
                      style={{
                        padding: '2px 6px',
                        borderRadius: 'var(--radius-sm)',
                        border: '1px solid var(--border)',
                        fontSize: 13,
                        marginLeft: 4,
                        background: isDone ? 'var(--success)' : task.status === 'in_progress' ? 'var(--warning)' : 'var(--bg)',
                        color: isDone ? 'white' : task.status === 'in_progress' ? 'white' : 'var(--text)',
                        fontWeight: 600,
                      }}
                    >
                      {STATUS_OPTIONS.map((s) => (
                        <option key={s} value={s}>{STATUS_LABELS[s]}</option>
                      ))}
                    </select>
                  </span>
                  {assigneeName && (
                    <span>Исполнитель: <strong>{assigneeName}</strong></span>
                  )}
                </div>

                {isDone && task.completion_comment && (
                  <div className="completion-info">
                    Комментарий: "{task.completion_comment}"
                  </div>
                )}

                <div className="task-card-actions">
                  {canComplete && (
                    <button className="btn btn-primary btn-sm" onClick={() => setCompleteTask(task)}>
                      Подтвердить выполнение
                    </button>
                  )}
                  {isAdmin && (
                    <button
                      className="btn btn-ghost btn-sm"
                      style={{ color: 'var(--danger)' }}
                      onClick={() => handleDelete(task.id)}
                    >
                      Удалить
                    </button>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      )}

      {showCreate && (
        <CreateTaskModal
          projectId={projectId}
          members={members}
          onClose={() => setShowCreate(false)}
          onCreated={() => { setShowCreate(false); load() }}
          onError={(msg) => setError(msg)}
        />
      )}

      {completeTask && (
        <CompleteTaskModal
          task={completeTask}
          onConfirm={(comment) => handleComplete(completeTask.id, comment)}
          onClose={() => setCompleteTask(null)}
        />
      )}
    </div>
  )
}

function CompleteTaskModal({ task, onConfirm, onClose }: {
  task: Task
  onConfirm: (comment: string) => void
  onClose: () => void
}) {
  const [comment, setComment] = useState('')
  const [saving, setSaving] = useState(false)

  const handleSubmit = async () => {
    setSaving(true)
    await onConfirm(comment)
    setSaving(false)
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal complete-modal" onClick={(e) => e.stopPropagation()} style={{ maxWidth: 480 }}>
        <button className="modal-close" onClick={onClose}>✕</button>
        <h2>Подтвердить выполнение</h2>
        <p style={{ color: 'var(--text-secondary)', marginBottom: 20, fontSize: 14 }}>
          Задача: <strong style={{ color: 'var(--text)' }}>{task.title}</strong>
        </p>
        <div className="form-group">
          <label>Комментарий (необязательно)</label>
          <textarea
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            placeholder="Напишите комментарий о выполненной работе..."
            style={{ width: '100%', padding: '10px 14px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border)', fontSize: 14, fontFamily: 'inherit', resize: 'vertical', minHeight: 100, background: 'var(--surface)', color: 'var(--text)' }}
          />
        </div>
        <div className="modal-actions">
          <button className="btn btn-secondary" onClick={onClose}>Отмена</button>
          <button className="btn btn-primary" onClick={handleSubmit} disabled={saving}>
            {saving ? 'Сохранение...' : 'Подтвердить'}
          </button>
        </div>
      </div>
    </div>
  )
}

function CreateTaskModal({ projectId, members, onClose, onCreated, onError }: {
  projectId: string
  members: Member[]
  onClose: () => void
  onCreated: () => void
  onError: (msg: string) => void
}) {
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [assignedTo, setAssignedTo] = useState<number | ''>('')
  const [priority, setPriority] = useState('medium')
  const [deadline, setDeadline] = useState('')
  const [saving, setSaving] = useState(false)

  const handleSubmit = async () => {
    if (!title.trim()) return
    setSaving(true)
    try {
      await api.createTask(projectId, {
        title: title.trim(),
        description: description.trim() || null,
        assigned_to: assignedTo || null,
        priority,
        deadline: deadline ? new Date(deadline).toISOString() : null,
      })
      onCreated()
    } catch (err) {
      onError(err instanceof Error ? err.message : 'Failed to create task')
    }
    setSaving(false)
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()} style={{ maxWidth: 480 }}>
        <button className="modal-close" onClick={onClose}>✕</button>
        <h2>Новая задача</h2>
        <div className="form-group">
          <label>Название *</label>
          <input type="text" value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Что нужно сделать?" />
        </div>
        <div className="form-group">
          <label>Описание</label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Подробное описание задачи"
            style={{ width: '100%', padding: '10px 14px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border)', fontSize: 14, fontFamily: 'inherit', resize: 'vertical', minHeight: 80 }}
          />
        </div>
        <div className="form-group">
          <label>Исполнитель</label>
          <select value={assignedTo} onChange={(e) => setAssignedTo(e.target.value ? Number(e.target.value) : '')} style={{ width: '100%', padding: '10px 14px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border)', fontSize: 14 }}>
            <option value="">Не назначен</option>
            {members.map((m) => (
              <option key={m.user_id} value={m.user_id}>{m.username} ({m.handle})</option>
            ))}
          </select>
        </div>
        <div className="form-group">
          <label>Приоритет</label>
          <select value={priority} onChange={(e) => setPriority(e.target.value)} style={{ width: '100%', padding: '10px 14px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border)', fontSize: 14 }}>
            {PRIORITY_OPTIONS.map((p) => (
              <option key={p} value={p}>{PRIORITY_LABELS[p]}</option>
            ))}
          </select>
        </div>
        <div className="form-group">
          <label>Дедлайн</label>
          <input type="datetime-local" value={deadline} onChange={(e) => setDeadline(e.target.value)} style={{ width: '100%', padding: '10px 14px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border)', fontSize: 14 }} />
        </div>
        <div className="modal-actions">
          <button className="btn btn-secondary" onClick={onClose}>Отмена</button>
          <button className="btn btn-primary" onClick={handleSubmit} disabled={saving || !title.trim()}>
            {saving ? 'Создание...' : 'Создать'}
          </button>
        </div>
      </div>
    </div>
  )
}