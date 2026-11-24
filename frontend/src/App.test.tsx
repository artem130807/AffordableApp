import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import App from './App'

const mocks = vi.hoisted(() => ({
  organizationTypes: vi.fn(),
  organizations: vi.fn(),
  createSearch: vi.fn(),
}))

vi.mock('./api/affordable', () => ({
  discoveryApi: {
    organizationTypes: mocks.organizationTypes,
    organizations: mocks.organizations,
    catalogs: vi.fn().mockResolvedValue([]),
    items: vi.fn().mockResolvedValue([]),
  },
  authApi: { me: vi.fn(), logout: vi.fn() },
  managementApi: {
    myOrganizations: vi.fn().mockResolvedValue([]),
    categories: vi.fn().mockResolvedValue([]),
    createOrganization: vi.fn(),
    createCatalog: vi.fn(),
    createCategory: vi.fn(),
    createItem: vi.fn(),
  },
}))
vi.mock('./api/searches', () => ({ searchApi: { create: mocks.createSearch } }))

describe('App', () => {
  beforeEach(() => {
    mocks.organizationTypes.mockResolvedValue([
      { id: 'restaurant', code: 'restaurant', name: 'Ресторан', description: null },
    ])
    mocks.organizations.mockResolvedValue([])
    mocks.createSearch.mockResolvedValue({
      filter: { id: 'filter', client_id: 'client', user_id: null, organization_type_id: null, budget: null, party_size: null, city: null, wishes: null, currency: 'RUB', created_at: '2026-01-01T00:00:00Z' },
      recommendations: [],
    })
  })

  it('loads discovery data and completes the skip-all flow', async () => {
    render(<App />)
    expect(await screen.findByRole('button', { name: /Ресторан/ })).toBeVisible()

    await userEvent.click(screen.getByRole('button', { name: 'Пропустить всё' }))

    expect(await screen.findByRole('heading', { name: 'Пока ничего не нашли' })).toBeVisible()
    expect(mocks.createSearch).toHaveBeenCalledWith({})
  })
})
