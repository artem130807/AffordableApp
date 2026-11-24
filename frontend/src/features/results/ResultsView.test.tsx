import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { ResultsView } from './ResultsView'

const organization = {
  id: 'org', type_id: 'restaurant', owner_id: 'owner', name: 'Тихий двор',
  description: null, address: null, city: 'Астрахань', latitude: null,
  longitude: null, is_active: true, created_at: '2026-01-01T00:00:00Z',
}
const item = {
  id: 'item', catalog_id: 'catalog', category_id: null, name: 'Ужин',
  description: null, price: '1800.00', currency: 'RUB', price_unit: 'item' as const,
  attributes: {}, is_available: true, created_at: '2026-01-01T00:00:00Z',
}

describe('ResultsView', () => {
  it('shows saved filters and opens a recommended organization', async () => {
    const onOpen = vi.fn()
    render(<ResultsView
      filter={{ id: 'filter', client_id: 'client', user_id: null, organization_type_id: 'restaurant', budget: '3000.00', party_size: 2, city: 'Астрахань', wishes: 'Тихо', currency: 'RUB', created_at: '2026-01-01T00:00:00Z' }}
      recommendations={[{ organization, suggested_items: [item], total: '1800.00', remaining_budget: '1200.00' }]}
      types={[{ id: 'restaurant', code: 'restaurant', name: 'Ресторан', description: null }]}
      onOpen={onOpen}
      onRestart={vi.fn()}
    />)

    expect(screen.getByText('до 3 000 ₽')).toBeVisible()
    expect(screen.getByText('Останется 1 200 ₽')).toBeVisible()
    await userEvent.click(screen.getByRole('button', { name: /Посмотреть вариант/ }))
    expect(onOpen).toHaveBeenCalledWith(organization, [item])
  })
})
