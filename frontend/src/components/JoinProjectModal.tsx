import { useState } from 'react'
import { api } from '../api/client'

type Props = {
  onClose: () => void
  onJoined: () => void
}

export default function JoinProjectModal({ onClose, onJoined }: Props) {
  const [invite, setInvite] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSubmitting(true)
    try {
      await api.joinProject(invite)
      onJoined()
      onClose()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to join project')
    }
    setSubmitting(false)
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>✕</button>
        <h2>Присоединиться к проекту</h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: 14, marginBottom: 20 }}>
          Вставьте ссылку-приглашение в формате <strong>UUID/SECRET_KEY</strong>
        </p>
        {error && <div className="form-error">{error}</div>}
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Ссылка-приглашение</label>
            <input type="text" value={invite} onChange={(e) => setInvite(e.target.value)} placeholder="550e8400-e29b-.../mysecret" required />
          </div>
          <div className="modal-actions">
            <button type="button" className="btn btn-secondary" onClick={onClose}>Отмена</button>
            <button type="submit" className="btn btn-primary" disabled={submitting}>
              {submitting ? 'Присоединение...' : 'Присоединиться'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
