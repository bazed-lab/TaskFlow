import { useEffect, useState } from 'react'
import { api } from '../api/client'

type CompletedTask = {
  id: number
  title: string
  description: string | null
  priority: string
  deadline: string | null
  completed_by: number
  completed_by_username: string
  completed_by_handle: string
  completed_at: string
  completion_comment: string | null
}

type Props = {
  projectId: string
  onClose: () => void
}

const PRIORITY_LABELS: Record<string, string> = {
  low: 'Низкий',
  medium: 'Средний',
  high: 'Высокий',
}

export default function CompletedTasks({ projectId, onClose }: Props) {
  const [tasks, setTasks] = useState<CompletedTask[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const load = async () => {
      setLoading(true)
      try {
        const data = await api.getCompletedTasks(projectId)
        setTasks(data)
      } catch {}
      setLoading(false)
    }
    load()
  }, [projectId])

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()} style={{ maxWidth: 560 }}>
        <button className="modal-close" onClick={onClose}>✕</button>
        <h2>Выполненные задачи ({tasks.length})</h2>

        {loading ? (
          <div style={{ textAlign: 'center', padding: 32 }}><div className="spinner" /></div>
        ) : tasks.length === 0 ? (
          <div className="empty-state" style={{ padding: '32px 0' }}>
            <p>Выполненных задач пока нет</p>
          </div>
        ) : (
          <div className="completed-list">
            {tasks.map((task) => (
              <div key={task.id} className="completed-task-item">
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
                  <h4>{task.title}</h4>
                  <span className={`task-priority task-priority-${task.priority}`}>
                    {PRIORITY_LABELS[task.priority]}
                  </span>
                </div>
                {task.description && (
                  <p style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 8 }}>{task.description}</p>
                )}
                <div className="completer-info">
                  Выполнил: <strong>{task.completed_by_username}</strong> ({task.completed_by_handle})
                  {' · '}
                  {new Date(task.completed_at).toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' })}
                </div>
                {task.completion_comment && (
                  <div className="completion-comment">
                    "{task.completion_comment}"
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        <div className="modal-actions">
          <button className="btn btn-secondary" onClick={onClose}>Закрыть</button>
        </div>
      </div>
    </div>
  )
}