import type { ApiErrorBody, TokenPair } from '../types'

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api/v1'
const STORAGE_KEY = 'affordable.auth'
const PUBLIC_AUTH_PATHS = new Set([
  '/auth/login',
  '/auth/register',
  '/auth/refresh',
  '/auth/logout',
])

function isTokenPair(value: unknown): value is TokenPair {
  if (typeof value !== 'object' || value === null) return false
  const candidate = value as Record<string, unknown>
  return (
    typeof candidate.access_token === 'string' && candidate.access_token.length > 0
    && typeof candidate.refresh_token === 'string' && candidate.refresh_token.length > 0
    && candidate.token_type === 'bearer'
  )
}

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
  ) {
    super(message)
  }
}

function readError(body: ApiErrorBody | null, fallback: string): string {
  if (typeof body?.detail === 'string') return body.detail
  if (Array.isArray(body?.detail)) {
    return body.detail.map((item) => item.msg).filter(Boolean).join(', ') || fallback
  }
  return fallback
}

class ApiClient {
  private tokens: TokenPair | null = this.restoreTokens()
  private refreshPromise: Promise<boolean> | null = null

  hasSession(): boolean {
    return this.tokens !== null
  }

  setTokens(tokens: TokenPair): void {
    this.tokens = tokens
    localStorage.setItem(STORAGE_KEY, JSON.stringify(tokens))
  }

  clearSession(): void {
    this.tokens = null
    localStorage.removeItem(STORAGE_KEY)
  }

  getRefreshToken(): string | null {
    return this.tokens?.refresh_token ?? null
  }

  async request<T>(path: string, init: RequestInit = {}, retry = true): Promise<T> {
    const headers = new Headers(init.headers)
    if (init.body && !headers.has('Content-Type')) headers.set('Content-Type', 'application/json')
    if (this.tokens && !PUBLIC_AUTH_PATHS.has(path)) {
      headers.set('Authorization', `Bearer ${this.tokens.access_token}`)
    }

    const response = await fetch(`${API_URL}${path}`, { ...init, headers })
    if (response.status === 401 && retry && this.tokens && !PUBLIC_AUTH_PATHS.has(path)) {
      if (await this.refreshSession()) return this.request<T>(path, init, false)
    }
    if (!response.ok) {
      const body = (await response.json().catch(() => null)) as ApiErrorBody | null
      throw new ApiError(readError(body, `Ошибка запроса (${response.status})`), response.status)
    }
    if (response.status === 204) return undefined as T
    return response.json() as Promise<T>
  }

  private restoreTokens(): TokenPair | null {
    try {
      const value = localStorage.getItem(STORAGE_KEY)
      if (!value) return null
      const parsed: unknown = JSON.parse(value)
      if (isTokenPair(parsed)) return parsed
      localStorage.removeItem(STORAGE_KEY)
      return null
    } catch {
      localStorage.removeItem(STORAGE_KEY)
      return null
    }
  }

  private async refreshSession(): Promise<boolean> {
    if (this.refreshPromise) return this.refreshPromise
    this.refreshPromise = (async () => {
      const refreshToken = this.tokens?.refresh_token
      if (!refreshToken) return false
      try {
        const response = await fetch(`${API_URL}/auth/refresh`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ refresh_token: refreshToken }),
        })
        if (!response.ok) throw new Error('Refresh failed')
        const tokens: unknown = await response.json()
        if (!isTokenPair(tokens)) throw new Error('Malformed refresh response')
        this.setTokens(tokens)
        return true
      } catch {
        this.clearSession()
        return false
      } finally {
        this.refreshPromise = null
      }
    })()
    return this.refreshPromise
  }
}

export const apiClient = new ApiClient()
