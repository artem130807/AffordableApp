import { useRef, useState, type FormEvent } from 'react'
import { managementApi } from '../api/affordable'
import { useManagementData } from '../features/management/useManagementData'
import type { CatalogItem, OrganizationType, User } from '../types'

interface ManagePanelProps {
  user: User
  types: OrganizationType[]
}

export function ManagePanel({ user, types }: ManagePanelProps) {
  const management = useManagementData()
  const {
    organizations, selectedOrganization, setSelectedOrganization,
    catalogs, selectedCatalog, setSelectedCatalog, categories, items,
    refreshOrganizations, refreshCatalogs, refreshCatalogData,
  } = management
  const [notice, setNotice] = useState('')
  const [mutationError, setMutationError] = useState('')
  const [mutationPending, setMutationPending] = useState(false)
  const mutationLock = useRef(false)
  const error = mutationError || management.error

  function beginMutation(): boolean {
    if (mutationLock.current) return false
    mutationLock.current = true
    setMutationPending(true)
    setMutationError('')
    management.clearError()
    setNotice('')
    return true
  }

  function endMutation() {
    mutationLock.current = false
    setMutationPending(false)
  }

  async function createOrganization(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); if (!beginMutation()) return
    const form = event.currentTarget
    const data = new FormData(form)
    try {
      const created = await managementApi.createOrganization({
        type_id: String(data.get('type_id')),
        name: String(data.get('name')),
        city: String(data.get('city')) || undefined,
        address: String(data.get('address')) || undefined,
        description: String(data.get('description')) || undefined,
      })
      form.reset(); await refreshOrganizations(created.id)
      setNotice('Организация опубликована')
    } catch (reason) { setMutationError(reason instanceof Error ? reason.message : 'Ошибка создания') }
    finally { endMutation() }
  }

  async function createCatalog(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); if (!selectedOrganization || !beginMutation()) return
    const form = event.currentTarget; const data = new FormData(form)
    try {
      const created = await managementApi.createCatalog(selectedOrganization, {
        name: String(data.get('name')),
        description: String(data.get('description')) || undefined,
      })
      form.reset(); await refreshCatalogs(created.id); setNotice('Каталог добавлен')
    } catch (reason) { setMutationError(reason instanceof Error ? reason.message : 'Ошибка создания') }
    finally { endMutation() }
  }

  async function createCategory(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); if (!selectedCatalog || !beginMutation()) return
    const form = event.currentTarget; const data = new FormData(form)
    try {
      await managementApi.createCategory(selectedCatalog, { name: String(data.get('name')) })
      form.reset(); await refreshCatalogData(); setNotice('Категория добавлена')
    } catch (reason) { setMutationError(reason instanceof Error ? reason.message : 'Ошибка создания') }
    finally { endMutation() }
  }

  async function createItem(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); if (!selectedCatalog || !beginMutation()) return
    const form = event.currentTarget; const data = new FormData(form)
    try {
      await managementApi.createItem(selectedCatalog, {
        name: String(data.get('name')),
        price: Number(data.get('price')),
        currency: 'RUB',
        price_unit: String(data.get('price_unit')) as CatalogItem['price_unit'],
        category_id: String(data.get('category_id')) || undefined,
        description: String(data.get('description')) || undefined,
      })
      form.reset(); await refreshCatalogData(); setNotice('Позиция добавлена')
    } catch (reason) { setMutationError(reason instanceof Error ? reason.message : 'Ошибка создания') }
    finally { endMutation() }
  }

  return (
    <main className="content-shell manage-page">
      <div className="section-heading">
        <div><p className="eyebrow">Кабинет партнёра</p><h1>{user.name}, управляйте местами</h1></div>
        <span className="user-chip">{organizations.length} организаций</span>
      </div>
      {(error || notice) && <div className={error ? 'notice notice--error' : 'notice'}>{error || notice}</div>}

      <div className="manage-grid">
        <aside className="panel organization-sidebar">
          <h2>Мои организации</h2>
          <div className="organization-list">
            {organizations.map((organization) => (
              <button className={selectedOrganization === organization.id ? 'selected' : ''} key={organization.id} onClick={() => setSelectedOrganization(organization.id)}>
                <span className="list-avatar">{organization.name.slice(0, 1)}</span>
                <span><strong>{organization.name}</strong><small>{organization.city || 'Город не указан'}</small></span>
              </button>
            ))}
            {!organizations.length && <p className="empty-copy">Пока пусто. Добавьте первое место.</p>}
          </div>
          <details className="create-details" open={!organizations.length}>
            <summary>+ Новая организация</summary>
            <form className="compact-form" onSubmit={createOrganization}>
              <input name="name" required placeholder="Название" />
              <select name="type_id" required defaultValue=""><option value="" disabled>Тип организации</option>{types.map((type) => <option value={type.id} key={type.id}>{type.name}</option>)}</select>
              <div className="field-row"><input name="city" placeholder="Город" /><input name="address" placeholder="Адрес" /></div>
              <textarea name="description" placeholder="Короткое описание" rows={2} />
              <button className="button button--primary" disabled={mutationPending}>Опубликовать</button>
            </form>
          </details>
        </aside>

        <section className="panel catalog-workspace">
          {!selectedOrganization ? <div className="empty-state"><span>⌂</span><h2>Выберите организацию</h2><p>Здесь появятся каталоги и позиции.</p></div> : <>
            <div className="workspace-header"><div><p className="eyebrow">Каталоги</p><h2>{organizations.find((item) => item.id === selectedOrganization)?.name}</h2></div><select value={selectedCatalog} onChange={(event) => setSelectedCatalog(event.target.value)}><option value="">Выберите каталог</option>{catalogs.map((catalog) => <option key={catalog.id} value={catalog.id}>{catalog.name}</option>)}</select></div>
            <details className="create-details"><summary>+ Добавить каталог</summary><form className="inline-form" onSubmit={createCatalog}><input name="name" required placeholder="Например, Основное меню" /><input name="description" placeholder="Описание" /><button className="button button--dark" disabled={mutationPending}>Добавить</button></form></details>
            {selectedCatalog && <>
              <div className="catalog-tools">
                <details className="create-details"><summary>+ Категория</summary><form className="inline-form" onSubmit={createCategory}><input name="name" required placeholder="Например, Десерты" /><button className="button button--dark" disabled={mutationPending}>Добавить</button></form></details>
                <details className="create-details"><summary>+ Позиция</summary><form className="item-form" onSubmit={createItem}><input name="name" required placeholder="Название" /><input name="price" type="number" min="0" step="0.01" required placeholder="Цена, ₽" /><select name="category_id"><option value="">Без категории</option>{categories.map((category) => <option key={category.id} value={category.id}>{category.name}</option>)}</select><select name="price_unit"><option value="item">За позицию</option><option value="person">За человека</option><option value="ticket">За билет</option><option value="hour">За час</option><option value="service">За услугу</option></select><input name="description" className="span-2" placeholder="Описание" /><button className="button button--primary" disabled={mutationPending}>Добавить позицию</button></form></details>
              </div>
              <div className="items-table"><div className="table-head"><span>Позиция</span><span>Категория</span><span>Цена</span></div>{items.map((item) => <div className="table-row" key={item.id}><span><strong>{item.name}</strong><small>{item.description || 'Без описания'}</small></span><span>{categories.find((category) => category.id === item.category_id)?.name || '—'}</span><span className="price">{Number(item.price).toLocaleString('ru-RU')} ₽</span></div>)}{!items.length && <p className="empty-copy">В каталоге пока нет позиций.</p>}</div>
            </>}
          </>}
        </section>
      </div>
    </main>
  )
}
