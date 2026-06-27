import { useEffect, useState } from 'react'
import { api } from '../api/client'
import type { User } from '../App'
import CreateProjectModal from './CreateProjectModal'
import JoinProjectModal from './JoinProjectModal'

type Props = {
  user: User
}

type Project = {
  id: string
  name: string
  description: string | null
  owner_id: number
  is_active: boolean
  created_at: string
}

export default function ProjectList({ user }: Props) {
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)
  const [showCreate, setShowCreate] = useState(false)
  const [showJoin, setShowJoin] = useState(false)

  const load = async () => {
    setLoading(true)
    try {
      const data = await api.getProjects()
      setProjects(data)
    } catch {
      // handled by client
    }
    setLoading(false)
  }

  useEffect(() => { load() }, [])

  const getRole = (project: Project) => {
    return project.owner_id === user.id ? 'admin' : 'member'
  }

  return (
    <div>
      <div className="page-header">
        <h1>Проекты</h1>
        <div style={{ display: 'flex', gap: 8 }}>
          <button className="btn btn-secondary" onClick={() => setShowJoin(true)}>
            + Присоединиться
          </button>
          <button className="btn btn-primary" onClick={() => setShowCreate(true)}>
            + Создать
          </button>
        </div>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: 48 }}><div className="spinner" /></div>
      ) : projects.length === 0 ? (
        <div className="empty-state">
          <h3>У вас пока нет проектов</h3>
          <p>Создайте первый проект или присоединитесь по приглашению</p>
          <button className="btn btn-primary" onClick={() => setShowCreate(true)}>
            + Создать проект
          </button>
        </div>
      ) : (
        <div className="project-grid">
          {projects.map((project) => (
            <div
              key={project.id}
              className="project-card"
              onClick={() => { window.location.hash = `#project/${project.id}` }}
            >
              <h3>{project.name}</h3>
              <p>{project.description || 'Нет описания'}</p>
              <div className="project-card-meta">
                <span className={`project-card-badge ${getRole(project) === 'admin' ? 'badge-admin' : 'badge-member'}`}>
                  {getRole(project) === 'admin' ? 'Админ' : 'Участник'}
                </span>
                <span>{new Date(project.created_at).toLocaleDateString('ru-RU')}</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {showCreate && (
        <CreateProjectModal
          onClose={() => setShowCreate(false)}
          onCreated={load}
        />
      )}

      {showJoin && (
        <JoinProjectModal
          onClose={() => setShowJoin(false)}
          onJoined={load}
        />
      )}
    </div>
  )
}
