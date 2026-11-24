import { beforeEach, describe, expect, it, vi } from 'vitest'

const tokens = {
  access_token: 'expired-access',
  refresh_token: 'valid-refresh',
  token_type: 'bearer',
}

const refreshedTokens = {
  access_token: 'fresh-access',
  refresh_token: 'fresh-refresh',
  token_type: 'bearer',
}

describe('ApiClient session refresh', () => {
  beforeEach(() => {
    vi.resetModules()
    localStorage.setItem('affordable.auth', JSON.stringify(tokens))
  })

  it('refreshes an expired access token before retrying auth/me', async () => {
    const fetchMock = vi
      .fn<typeof fetch>()
      .mockResolvedValueOnce(new Response(JSON.stringify({ detail: 'expired' }), { status: 401 }))
      .mockResolvedValueOnce(
        new Response(JSON.stringify(refreshedTokens), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        }),
      )
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ id: 'user-1', name: 'Мария' }), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        }),
      )
    vi.stubGlobal('fetch', fetchMock)
    const { apiClient } = await import('./client')

    const user = await apiClient.request<{ id: string }>('/auth/me')

    expect(user.id).toBe('user-1')
    expect(fetchMock).toHaveBeenCalledTimes(3)
    expect(fetchMock.mock.calls[1]?.[0]).toContain('/auth/refresh')
    expect(fetchMock.mock.calls[2]?.[1]?.headers).toBeInstanceOf(Headers)
    expect((fetchMock.mock.calls[2]?.[1]?.headers as Headers).get('Authorization')).toBe(
      'Bearer fresh-access',
    )
  })

  it('shares one refresh request between concurrent unauthorized calls', async () => {
    let refreshResolve: ((response: Response) => void) | undefined
    const fetchMock = vi.fn<typeof fetch>((input, init) => {
      const url = String(input)
      if (url.endsWith('/auth/refresh')) {
        return new Promise<Response>((resolve) => { refreshResolve = resolve })
      }
      const authorization = (init?.headers as Headers | undefined)?.get?.('Authorization')
      if (authorization === 'Bearer fresh-access') {
        return Promise.resolve(new Response(JSON.stringify({ ok: true }), { status: 200 }))
      }
      return Promise.resolve(new Response(JSON.stringify({ detail: 'expired' }), { status: 401 }))
    })
    vi.stubGlobal('fetch', fetchMock)
    const { apiClient } = await import('./client')

    const first = apiClient.request('/organizations')
    const second = apiClient.request('/organization-types')
    await vi.waitFor(() => expect(refreshResolve).toBeTypeOf('function'))
    refreshResolve?.(new Response(JSON.stringify(refreshedTokens), { status: 200 }))
    await Promise.all([first, second])

    expect(fetchMock.mock.calls.filter(([url]) => String(url).endsWith('/auth/refresh'))).toHaveLength(1)
  })

  it('discards a malformed token object restored from localStorage', async () => {
    localStorage.setItem('affordable.auth', JSON.stringify({ access_token: 42 }))
    const { apiClient } = await import('./client')

    expect(apiClient.hasSession()).toBe(false)
    expect(localStorage.getItem('affordable.auth')).toBeNull()
  })

  it('rejects a malformed refresh response without retrying the request', async () => {
    const fetchMock = vi
      .fn<typeof fetch>()
      .mockResolvedValueOnce(new Response(JSON.stringify({ detail: 'expired' }), { status: 401 }))
      .mockResolvedValueOnce(new Response(JSON.stringify({ access_token: 'missing-fields' }), { status: 200 }))
    vi.stubGlobal('fetch', fetchMock)
    const { apiClient } = await import('./client')

    await expect(apiClient.request('/auth/me')).rejects.toMatchObject({ status: 401 })
    expect(fetchMock).toHaveBeenCalledTimes(2)
    expect(apiClient.hasSession()).toBe(false)
  })

  it('does not refresh or attach access credentials to logout', async () => {
    const fetchMock = vi.fn<typeof fetch>().mockResolvedValue(
      new Response(JSON.stringify({ detail: 'already logged out' }), { status: 401 }),
    )
    vi.stubGlobal('fetch', fetchMock)
    const { apiClient } = await import('./client')

    await expect(apiClient.request('/auth/logout', { method: 'POST' })).rejects.toMatchObject({
      status: 401,
    })
    expect(fetchMock).toHaveBeenCalledTimes(1)
    expect((fetchMock.mock.calls[0]?.[1]?.headers as Headers).has('Authorization')).toBe(false)
  })
})
