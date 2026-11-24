import type { RecommendationFilterDraft, RecommendationSearch } from '../types'
import { getClientId } from '../session/clientId'
import { apiClient } from './client'

export const searchApi = {
  create(draft: RecommendationFilterDraft): Promise<RecommendationSearch> {
    return apiClient.request<RecommendationSearch>('/recommendation-searches', {
      method: 'POST',
      body: JSON.stringify({
        client_id: getClientId(),
        currency: 'RUB',
        ...draft,
      }),
    })
  },
}
