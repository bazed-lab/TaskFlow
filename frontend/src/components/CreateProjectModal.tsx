import { useState } from 'react'
import { api } from '../api/client'

type Props = {
  onClose: () => void
  onCreated: () => void
}

export default function CreateProjectModal({ onClose, onCreated }: Props) {
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [secretKey, setSecretKey] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSubmitting(true)
    try {
      await api.createProject({
        name,
        description: description || null,
        secret_key: secretKey || null,
      })
      onCreated()
      onClose()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create project')
    }
    setSubmitting(false)
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>✕</button>
        <h2>Создать проект</h2>
        {error && <div className="form-error">{error}</div>}
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Название</label>
            <input type="text" value={name} onChange={(e) => setName(e.target.value)} placeholder="Название проекта" required />
          </div>
          <div className="form-group">
            <label>Описание</label>
            <input type="text" value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Описание (необязательно)" />
          </div>
          <div className="form-group">
            <label>Секретный ключ для приглашений</label>
            <input type="text" value={secretKey} onChange={(e) => setSecretKey(e.target.value)} placeholder="Мой секрет (необязательно)" />
          </div>
          <div className="modal-actions">
            <button type="button" className="btn btn-secondary" onClick={onClose}>Отмена</button>
            <button type="submit" className="btn btn-primary" disabled={submitting}>
              {submitting ? 'Создание...' : 'Создать'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
