import { apiClient } from './client'
import type {
  Catalog,
  CatalogItem,
  Category,
  Organization,
  OrganizationType,
  Recommendation,
  TokenPair,
  User,
} from '../types'

const json = (value: unknown) => JSON.stringify(value)

async function login(email: string, password: string): Promise<User> {
  const tokens = await apiClient.request<TokenPair>('/auth/login', {
    method: 'POST',
    body: json({ email, password }),
  })
  apiClient.setTokens(tokens)
  return apiClient.request<User>('/auth/me')
}

export const authApi = {
  login,
  async register(name: string, email: string, password: string): Promise<User> {
    await apiClient.request<User>('/auth/register', {
      method: 'POST',
      body: json({ name, email, password }),
    })
    return login(email, password)
  },
  me: () => apiClient.request<User>('/auth/me'),
  async logout(): Promise<void> {
    const refreshToken = apiClient.getRefreshToken()
    try {
      if (refreshToken) {
        await apiClient.request<void>('/auth/logout', {
          method: 'POST',
          body: json({ refresh_token: refreshToken }),
        })
      }
    } finally {
      apiClient.clearSession()
    }
  },
}

export const discoveryApi = {
  organizationTypes: () => apiClient.request<OrganizationType[]>('/organization-types'),
  organizations: (params = new URLSearchParams()) =>
    apiClient.request<Organization[]>(`/organizations?${params.toString()}`),
  recommendations(params: URLSearchParams) {
    return apiClient.request<Recommendation[]>(`/recommendations?${params.toString()}`)
  },
  catalogs: (organizationId: string) =>
    apiClient.request<Catalog[]>(`/organizations/${organizationId}/catalogs`),
  items: (catalogId: string) => apiClient.request<CatalogItem[]>(`/catalogs/${catalogId}/items`),
}

export const managementApi = {
  myOrganizations: () => apiClient.request<Organization[]>('/organizations/mine'),
  createOrganization: (payload: {
    type_id: string
    name: string
    city?: string
    address?: string
    description?: string
  }) => apiClient.request<Organization>('/organizations', { method: 'POST', body: json(payload) }),
  createCatalog: (organizationId: string, payload: { name: string; description?: string }) =>
    apiClient.request<Catalog>(`/organizations/${organizationId}/catalogs`, {
      method: 'POST',
      body: json(payload),
    }),
  categories: (catalogId: string) =>
    apiClient.request<Category[]>(`/catalogs/${catalogId}/categories`),
  createCategory: (catalogId: string, payload: { name: string; description?: string }) =>
    apiClient.request<Category>(`/catalogs/${catalogId}/categories`, {
      method: 'POST',
      body: json(payload),
    }),
  createItem: (
    catalogId: string,
    payload: {
      name: string
      price: number
      currency: string
      price_unit: CatalogItem['price_unit']
      category_id?: string
      description?: string
    },
  ) =>
    apiClient.request<CatalogItem>(`/catalogs/${catalogId}/items`, {
      method: 'POST',
      body: json(payload),
    }),
}
