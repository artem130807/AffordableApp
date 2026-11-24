import type { CatalogItem, Organization, OrganizationType, Recommendation, RecommendationFilter } from '../../types'
import { findType, formatMoney } from '../../ui'

export function ResultsView({ filter, recommendations, types, onOpen, onRestart }: {
  filter: RecommendationFilter
  recommendations: Recommendation[]
  types: OrganizationType[]
  onOpen: (organization: Organization, items: CatalogItem[]) => void
  onRestart: () => void
}) {
  return <main className="content-shell results-page">
    <div className="results-intro"><div><p className="eyebrow">Подбор готов</p><h1>{recommendations.length ? 'Вот что подойдёт' : 'Пока ничего не нашли'}</h1><p>{recommendations.length ? 'Собрали варианты по вашим ответам и актуальным позициям каталогов.' : 'Попробуйте новый подбор: измените бюджет, город или пожелания.'}</p></div><button className="button button--primary" onClick={onRestart}>Новый подбор</button></div>
    <div className="filter-summary" aria-label="Параметры поиска">
      {filter.budget && <span>до {formatMoney(filter.budget)}</span>}
      {filter.party_size && <span>{filter.party_size} чел.</span>}
      {filter.city && <span>{filter.city}</span>}
      {filter.wishes && <span>{filter.wishes}</span>}
      {!filter.budget && !filter.party_size && !filter.city && !filter.wishes && <span>Без ограничений</span>}
    </div>
    {recommendations.length ? <div className="recommendations-grid">{recommendations.map((item, index) => <RecommendationCard key={item.organization.id} recommendation={item} type={findType(item.organization.type_id, types)} featured={index === 0} onOpen={() => onOpen(item.organization, item.suggested_items)} />)}</div> : <div className="empty-state"><span>⌕</span><h2>Подходящих вариантов нет</h2><p>Новые организации и предложения появляются регулярно.</p></div>}
  </main>
}

function RecommendationCard({ recommendation, type, featured, onOpen }: { recommendation: Recommendation; type?: OrganizationType; featured: boolean; onOpen: () => void }) {
  return <article className={`recommendation-card ${featured ? 'recommendation-card--featured' : ''}`}>{featured && <span className="best-badge">Лучшее совпадение</span>}<div className="recommendation-top"><div className="recommendation-logo">{recommendation.organization.name.slice(0, 1)}</div><div><span className="meta-line">{type?.name || 'Организация'} · {recommendation.organization.city || 'Онлайн'}</span><h3>{recommendation.organization.name}</h3></div></div><div className="suggested-list">{recommendation.suggested_items.slice(0, 4).map((item) => <div key={item.id}><span>{item.name}<small>{item.price_unit === 'person' ? 'за человека' : 'за позицию'}</small></span><strong>{formatMoney(item.price)}</strong></div>)}</div><div className="total-row"><span>Итого<strong>{formatMoney(recommendation.total)}</strong></span>{recommendation.remaining_budget !== null && <span className="remaining">Останется {formatMoney(recommendation.remaining_budget)}</span>}</div><button className="button button--dark button--wide" onClick={onOpen}>Посмотреть вариант <span>→</span></button></article>
}
