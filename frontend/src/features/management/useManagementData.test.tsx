import { act, renderHook, waitFor } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import type { Catalog, Organization } from '../../types'
import { useManagementData, type ManagementDataApi } from './useManagementData'

const organization = (id: string): Organization => ({
  id, type_id: 'type', owner_id: 'owner', name: id, description: null,
  address: null, city: null, latitude: null, longitude: null,
  is_active: true, created_at: '2026-01-01T00:00:00Z',
})

const catalog = (id: string, organizationId: string): Catalog => ({
  id, organization_id: organizationId, name: id, description: null,
  is_active: true, created_at: '2026-01-01T00:00:00Z',
})

describe('useManagementData', () => {
  it('ignores catalogs returned for an organization that is no longer selected', async () => {
    let resolveFirst!: (value: Catalog[]) => void
    const api: ManagementDataApi = {
      organizations: vi.fn().mockResolvedValue([organization('first'), organization('second')]),
      catalogs: vi.fn((id: string) => id === 'first'
        ? new Promise<Catalog[]>((resolve) => { resolveFirst = resolve })
        : Promise.resolve([catalog('second-catalog', 'second')])),
      categories: vi.fn().mockResolvedValue([]),
      items: vi.fn().mockResolvedValue([]),
    }
    const { result } = renderHook(() => useManagementData(api))
    await waitFor(() => expect(result.current.selectedOrganization).toBe('first'))

    act(() => result.current.setSelectedOrganization('second'))
    await waitFor(() => expect(result.current.catalogs[0]?.id).toBe('second-catalog'))
    await act(async () => { resolveFirst([catalog('stale-catalog', 'first')]); await Promise.resolve() })

    expect(result.current.selectedOrganization).toBe('second')
    expect(result.current.catalogs.map((item) => item.id)).toEqual(['second-catalog'])
  })
})
