import { useEffect } from 'react'
import type { CatalogItem, Organization, OrganizationType } from '../types'
import { formatMoney, typeMeta } from '../ui'

export function PlaceModal({ organization, type, items, isLoading = false, error = '', onClose }: {
  organization: Organization
  type?: OrganizationType
  items: CatalogItem[]
  isLoading?: boolean
  error?: string
  onClose: () => void
}) {
  useEffect(() => {
    const previousOverflow = document.body.style.overflow
    const handleKey = (event: KeyboardEvent) => { if (event.key === 'Escape') onClose() }
    document.body.style.overflow = 'hidden'
    document.addEventListener('keydown', handleKey)
    return () => { document.body.style.overflow = previousOverflow; document.removeEventListener('keydown', handleKey) }
  }, [onClose])

  return <div className="modal-backdrop" role="presentation" onMouseDown={onClose}><section className="place-modal" role="dialog" aria-modal="true" aria-label={organization.name} onMouseDown={(event) => event.stopPropagation()}><button className="icon-button modal-close" onClick={onClose} aria-label="Закрыть">×</button><div className="place-modal-cover"><span>{typeMeta[type?.code || '']?.icon || '○'}</span><small>{type?.name || 'Организация'}</small></div><div className="place-modal-body"><p className="eyebrow">{organization.city || 'Организация'}</p><h2>{organization.name}</h2><p className="muted">{organization.description || 'Каталог актуальных предложений организации.'}</p>{organization.address && <p className="address-line">⌖ {organization.address}</p>}<h3>Каталог</h3>{error && <div className="notice notice--error">{error}</div>}<div className="modal-items">{isLoading ? <p className="empty-copy">Загружаем каталог…</p> : items.map((item) => <div key={item.id}><span><strong>{item.name}</strong><small>{item.description || 'Доступно сейчас'}</small></span><b>{formatMoney(item.price)}</b></div>)}{!isLoading && !items.length && !error && <p className="empty-copy">Позиции пока не добавлены.</p>}</div></div></section></div>
}
