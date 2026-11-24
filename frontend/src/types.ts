export interface Permission {
  id: string
  code: string
  name: string
  description: string | null
}

export interface Role {
  id: string
  name: string
  description: string | null
  permissions: Permission[]
}

export interface User {
  id: string
  email: string
  name: string
  is_active: boolean
  roles: Role[]
}

export interface TokenPair {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface OrganizationType {
  id: string
  code: string
  name: string
  description: string | null
}

export interface Organization {
  id: string
  type_id: string
  owner_id: string
  name: string
  description: string | null
  address: string | null
  city: string | null
  latitude: string | null
  longitude: string | null
  is_active: boolean
  created_at: string
}

export interface Catalog {
  id: string
  organization_id: string
  name: string
  description: string | null
  is_active: boolean
  created_at: string
}

export interface Category {
  id: string
  catalog_id: string
  name: string
  description: string | null
}

export interface CatalogItem {
  id: string
  catalog_id: string
  category_id: string | null
  name: string
  description: string | null
  price: string
  currency: string
  price_unit: 'item' | 'person' | 'hour' | 'ticket' | 'service'
  attributes: Record<string, unknown>
  is_available: boolean
  created_at: string
}

export interface Recommendation {
  organization: Organization
  suggested_items: CatalogItem[]
  total: string
  remaining_budget: string | null
}

export interface RecommendationFilterDraft {
  organization_type_id?: string
  budget?: number
  party_size?: number
  city?: string
  wishes?: string
}

export interface RecommendationFilter {
  id: string
  client_id: string
  user_id: string | null
  organization_type_id: string | null
  budget: string | null
  party_size: number | null
  city: string | null
  wishes: string | null
  currency: string
  created_at: string
}

export interface RecommendationSearch {
  filter: RecommendationFilter
  recommendations: Recommendation[]
}

export interface ApiErrorBody {
  detail?: string | Array<{ msg?: string }>
}
