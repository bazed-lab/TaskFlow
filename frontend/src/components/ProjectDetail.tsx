import { useEffect, useState } from 'react'
import { api } from '../api/client'
import type { User } from '../App'
import MemberProfileModal from './MemberProfileModal'
import TaskList from './TaskList'
import CompletedTasks from './CompletedTasks'

type Props = {
  projectId: string
  user: User
}

type Project = {
  id: string
  name: string
  description: string | null
  secret_key: string | null
  owner_id: number
  is_active: boolean
  created_at: string
}

type Member = {
  id: number
  user_id: number
  role: string
  username: string
  handle: string
}

type SidebarTab = 'tasks' | 'members'

export default function ProjectDetail({ projectId, user }: Props) {
  const [project, setProject] = useState<Project | null>(null)
  const [members, setMembers] = useState<Member[]>([])
  const [loading, setLoading] = useState(true)
  const [inviteCopied, setInviteCopied] = useState(false)
  const [addHandle, setAddHandle] = useState('')
  const [addRole, setAddRole] = useState<'admin' | 'member'>('member')
  const [showAdd, setShowAdd] = useState(false)
  const [error, setError] = useState('')
  const [profileMember, setProfileMember] = useState<Member | null>(null)
  const [showCompleted, setShowCompleted] = useState(false)
  const [tab, setTab] = useState<SidebarTab>('tasks')

  const load = async () => {
    setLoading(true)
    setError('')
    try {
      const data = await api.getProject(projectId)
      setProject(data.project)
      setMembers(data.members)
    } catch {
      setProject(null)
    }
    setLoading(false)
  }

  useEffect(() => { load() }, [projectId])

  const isAdmin = members.find((m) => m.user_id === user.id)?.role === 'admin'

  const handleCopyInvite = () => {
    navigator.clipboard.writeText(`${projectId}/${project?.secret_key || 'secret'}`)
    setInviteCopied(true)
    setTimeout(() => setInviteCopied(false), 2000)
  }

  const handleAddMember = async () => {
    setError('')
    try {
      await api.addMember(projectId, { handle: addHandle, role: addRole })
      setAddHandle('')
      setShowAdd(false)
      load()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add member')
    }
  }

  const handleRemoveMember = async (userId: number) => {
    if (!confirm('Удалить участника?')) return
    try {
      await api.removeMember(projectId, userId)
      load()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to remove member')
    }
  }

  const handleToggleRole = async (member: Member) => {
    const newRole = member.role === 'admin' ? 'member' : 'admin'
    try {
      await api.updateMemberRole(projectId, member.user_id, { role: newRole })
      load()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update role')
    }
  }

  if (loading) {
    return <div style={{ textAlign: 'center', padding: 48 }}><div className="spinner" /></div>
  }

  if (!project) {
    return (
      <div>
        <button className="back-link" onClick={() => { window.location.hash = '#projects' }}>
          ← Назад к проектам
        </button>
        <div className="empty-state">
          <h3>Проект не найден</h3>
        </div>
      </div>
    )
  }

  return (
    <div>
      <button className="back-link" onClick={() => { window.location.hash = '#projects' }}>
        ← Назад к проектам
      </button>

      <div className="project-detail-header" style={{ marginBottom: 24 }}>
        <div>
          <h1>{project.name}</h1>
          {project.description && (
            <p style={{ color: 'var(--text-secondary)', fontSize: 15, marginTop: 8 }}>{project.description}</p>
          )}
        </div>
        {isAdmin && (
          <div className="project-detail-actions">
            <button className="btn btn-secondary btn-sm" onClick={handleCopyInvite}>
              {inviteCopied ? 'Скопировано!' : 'Копировать ссылку'}
            </button>
          </div>
        )}
      </div>

      {error && <div className="form-error" style={{ marginBottom: 16 }}>{error}</div>}

      <div className="project-layout">
        <div className="project-main">
          {tab === 'tasks' && (
            <TaskList
              projectId={projectId}
              isAdmin={isAdmin}
              members={members}
              currentUserId={user.id}
            />
          )}

          {tab === 'members' && (
            <div>
              <div className="section-header">
                <h2>Участники ({members.length})</h2>
                {isAdmin && (
                  <button className="btn btn-primary btn-sm" onClick={() => setShowAdd(true)}>
                    + Добавить
                  </button>
                )}
              </div>
              <div className="member-list">
                {members.map((member) => {
                  const isOwner = member.user_id === project.owner_id
                  return (
                    <div key={member.id} className="member-item">
                      <div className="member-item-info">
                        <span className={`project-card-badge ${member.role === 'admin' ? 'badge-admin' : 'badge-member'}`}>
                          {member.role === 'admin' ? 'Админ' : 'Участник'}
                        </span>
                        <button className="member-item-username" onClick={() => setProfileMember(member)}>
                          {member.username}
                        </button>
                        <span className="member-item-handle">{member.handle}</span>
                        {isOwner && <span className="project-card-badge badge-admin">Владелец</span>}
                      </div>
                      {isAdmin && member.user_id !== user.id && (
                        <div className="member-item-actions">
                          <button className="btn btn-ghost btn-sm" onClick={() => handleToggleRole(member)}>
                            {member.role === 'admin' ? 'Сделать участником' : 'Сделать админом'}
                          </button>
                          {!isOwner && (
                            <button className="btn btn-ghost btn-sm" style={{ color: 'var(--danger)' }} onClick={() => handleRemoveMember(member.user_id)}>
                              Удалить
                            </button>
                          )}
                        </div>
                      )}
                    </div>
                  )
                })}
              </div>
            </div>
          )}
        </div>

        <div className="project-sidebar">
          <button
            className={`btn btn-secondary ${tab === 'tasks' ? 'active' : ''}`}
            onClick={() => setTab('tasks')}
          >
            📋 Задачи
          </button>
          <button
            className={`btn btn-secondary ${tab === 'members' ? 'active' : ''}`}
            onClick={() => setTab('members')}
          >
            👥 Участники
          </button>
          <button
            className="btn btn-secondary"
            onClick={() => setShowCompleted(true)}
          >
            ✅ Выполненные
          </button>
        </div>
      </div>

      {isAdmin && (
        <div className="invite-link-box" style={{ marginTop: 24 }}>
          <code>{projectId}/{project.secret_key || 'secret'}</code>
          <button className="btn btn-secondary btn-sm" onClick={handleCopyInvite}>
            {inviteCopied ? 'Скопировано' : 'Копировать'}
          </button>
        </div>
      )}

      {showAdd && (
        <div className="modal-overlay" onClick={() => setShowAdd(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()} style={{ maxWidth: 400 }}>
            <button className="modal-close" onClick={() => setShowAdd(false)}>✕</button>
            <h2>Добавить участника</h2>
            <div className="form-group">
              <label>Handle пользователя</label>
              <input type="text" value={addHandle} onChange={(e) => setAddHandle(e.target.value)} placeholder="@username" />
            </div>
            <div className="form-group">
              <label>Роль</label>
              <select value={addRole} onChange={(e) => setAddRole(e.target.value as 'admin' | 'member')} style={{ width: '100%', padding: '10px 14px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border)', fontSize: 14 }}>
                <option value="member">Участник</option>
                <option value="admin">Админ</option>
              </select>
            </div>
            <div className="modal-actions">
              <button className="btn btn-secondary" onClick={() => setShowAdd(false)}>Отмена</button>
              <button className="btn btn-primary" onClick={handleAddMember}>Добавить</button>
            </div>
          </div>
        </div>
      )}

      {profileMember && (
        <MemberProfileModal
          member={profileMember}
          isOwner={profileMember.user_id === project.owner_id}
          onClose={() => setProfileMember(null)}
        />
      )}

      {showCompleted && (
        <CompletedTasks
          projectId={projectId}
          onClose={() => setShowCompleted(false)}
        />
      )}
    </div>
  )
}