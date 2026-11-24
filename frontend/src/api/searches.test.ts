import { beforeEach, describe, expect, it, vi } from 'vitest'

describe('searchApi', () => {
  beforeEach(() => vi.resetModules())

  it('adds a stable anonymous client id to a persisted search', async () => {
    const response = { filter: {}, recommendations: [] }
    const fetchMock = vi.fn<typeof fetch>().mockResolvedValue(
      new Response(JSON.stringify(response), { status: 201 }),
    )
    vi.stubGlobal('fetch', fetchMock)
    const { searchApi } = await import('./searches')

    await searchApi.create({ budget: 2500 })

    const body = JSON.parse(String(fetchMock.mock.calls[0]?.[1]?.body)) as Record<string, unknown>
    expect(body.budget).toBe(2500)
    expect(body.currency).toBe('RUB')
    expect(body.client_id).toMatch(/^[0-9a-f-]{36}$/)
  })
})
