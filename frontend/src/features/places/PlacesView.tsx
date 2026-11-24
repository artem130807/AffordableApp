import type { Organization, OrganizationType } from '../../types'
import { findType, typeMeta } from '../../ui'

export function PlacesView({ organizations, types, error, onOpen }: { organizations: Organization[]; types: OrganizationType[]; error?: string; onOpen: (organization: Organization) => void }) {
  return <main className="content-shell places-page"><div className="section-heading"><div><p className="eyebrow">Каталог города</p><h1>Места для ваших планов</h1><p className="muted">Рестораны, театры, развлечения и магазины в одном месте.</p></div><span className="count-badge">{organizations.length} мест</span></div>{error && <div className="notice notice--error">{error}</div>}<div className="places-grid">{organizations.map((organization) => <PlaceCard key={organization.id} organization={organization} type={findType(organization.type_id, types)} onOpen={() => onOpen(organization)} />)}</div>{!organizations.length && <div className="empty-state"><span>⌕</span><h2>Организаций пока нет</h2><p>Каталог скоро пополнится.</p></div>}</main>
}

function PlaceCard({ organization, type, onOpen }: { organization: Organization; type?: OrganizationType; onOpen: () => void }) {
  const meta = typeMeta[type?.code || ''] || { icon: '○', color: 'blue' }
  return <button className="place-card" onClick={onOpen}><div className={`place-visual place-visual--${meta.color}`}><span>{meta.icon}</span><small>{type?.name || 'Организация'}</small></div><div className="place-card-body"><h3>{organization.name}</h3><p>{organization.description || 'Откройте каталог и выберите подходящий вариант.'}</p><div><span>⌖ {organization.city || 'Город не указан'}</span><strong>Подробнее →</strong></div></div></button>
}
