type Member = {
  id: number
  user_id: number
  role: string
  username: string
  handle: string
}

type Props = {
  member: Member
  isOwner: boolean
  onClose: () => void
}

function getInitials(name: string): string {
  return name.slice(0, 2).toUpperCase()
}

export default function MemberProfileModal({ member, isOwner, onClose }: Props) {
  const roleLabel = member.role === 'admin' ? 'Админ' : 'Участник'

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal member-profile-modal" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>✕</button>
        <div className="member-profile-avatar">
          {getInitials(member.username)}
        </div>
        <h2 className="member-profile-name">{member.username}</h2>
        <p className="member-profile-handle">{member.handle}</p>
        <div className="member-profile-role" style={{ marginTop: 12 }}>
          <span className={`project-card-badge ${member.role === 'admin' ? 'badge-admin' : 'badge-member'}`}>
            {roleLabel}
          </span>
          {isOwner && <span className="project-card-badge badge-admin">Владелец</span>}
        </div>
      </div>
    </div>
  )
}
