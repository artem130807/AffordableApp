import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { ManagePanel } from './ManagePanel'

const api = vi.hoisted(() => ({
  myOrganizations: vi.fn().mockResolvedValue([]),
  createOrganization: vi.fn(),
  catalogs: vi.fn().mockResolvedValue([]),
  categories: vi.fn().mockResolvedValue([]),
  items: vi.fn().mockResolvedValue([]),
}))

vi.mock('../api/affordable', () => ({
  discoveryApi: { catalogs: api.catalogs, items: api.items },
  managementApi: {
    myOrganizations: api.myOrganizations,
    createOrganization: api.createOrganization,
    categories: api.categories,
  },
}))

describe('ManagePanel', () => {
  it('does not submit a create mutation twice while the first request is pending', async () => {
    api.createOrganization.mockReturnValue(new Promise(() => undefined))
    render(<ManagePanel
      user={{ id: 'user', email: 'u@example.com', name: 'User', is_active: true, roles: [] }}
      types={[{ id: 'restaurant', code: 'restaurant', name: 'Ресторан', description: null }]}
    />)
    await userEvent.type(screen.getByPlaceholderText('Название'), 'Новое место')
    await userEvent.selectOptions(screen.getByRole('combobox', { name: '' }), 'restaurant')

    await userEvent.dblClick(screen.getByRole('button', { name: 'Опубликовать' }))

    expect(api.createOrganization).toHaveBeenCalledTimes(1)
  })
})
