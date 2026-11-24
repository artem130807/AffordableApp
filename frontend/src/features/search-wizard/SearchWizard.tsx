import { useReducer, useRef, useState } from 'react'
import type { OrganizationType, RecommendationFilterDraft } from '../../types'
import { OptionStep } from './steps/OptionStep'
import { NumberStep } from './steps/NumberStep'
import { TextStep } from './steps/TextStep'
import { initialWizardState, wizardReducer, wizardSteps } from './wizardState'

interface SearchWizardProps {
  types: OrganizationType[]
  cities: string[]
  isLoadingTypes?: boolean
  discoveryError?: string
  onComplete: (draft: RecommendationFilterDraft) => Promise<void>
}

const typeIcons: Record<string, string> = {
  restaurant: '⌁',
  theater: '◐',
  electronics_store: '◇',
  entertainment: '✦',
}

export function SearchWizard({ types, cities, isLoadingTypes = false, discoveryError = '', onComplete }: SearchWizardProps) {
  const [state, dispatch] = useReducer(wizardReducer, initialWizardState)
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const lastDraft = useRef<RecommendationFilterDraft>({})
  const submitLock = useRef(false)
  const step = wizardSteps[state.stepIndex]

  async function complete(draft: RecommendationFilterDraft) {
    if (submitLock.current) return
    submitLock.current = true
    lastDraft.current = draft
    setError('')
    setIsSubmitting(true)
    try {
      await onComplete(draft)
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Не удалось выполнить поиск')
      submitLock.current = false
    } finally {
      setIsSubmitting(false)
    }
  }

  function answer(field: keyof RecommendationFilterDraft, value: string | number) {
    const draft = { ...state.draft, [field]: value }
    dispatch({ type: 'answer', field, value })
    if (state.stepIndex === wizardSteps.length - 1) void complete(draft)
  }

  function skip() {
    dispatch({ type: 'skip' })
    if (state.stepIndex === wizardSteps.length - 1) void complete(state.draft)
  }

  if (isSubmitting) {
    return <section className="search-wizard search-wizard--status" aria-live="polite"><div className="wizard-loader" /><h1>Подбираем варианты…</h1><p>Сохраняем ответы и сравниваем предложения.</p></section>
  }

  if (error) {
    return <section className="search-wizard search-wizard--status" role="alert"><span className="wizard-status-icon">↻</span><h1>Не получилось выполнить поиск</h1><p>{error}</p><button className="wizard-primary wizard-primary--compact" onClick={() => void complete(lastDraft.current)}>Попробовать ещё раз</button></section>
  }

  return (
    <section className="search-wizard" aria-labelledby="wizard-question">
      <header className="wizard-header">
        <div className="brand"><span className="brand-mark">А</span><span>Affordable</span></div>
        <button className="wizard-skip-all" type="button" onClick={() => { dispatch({ type: 'skip_all' }); void complete({}) }}>Пропустить всё</button>
      </header>

      <div className="wizard-progress" aria-label={`Шаг ${state.stepIndex + 1} из ${wizardSteps.length}`}>
        <span>{state.stepIndex + 1} из {wizardSteps.length}</span>
        <div>{wizardSteps.map((item, index) => <i className={index <= state.stepIndex ? 'active' : ''} key={item} />)}</div>
      </div>

      <div className="wizard-content">
        {step === 'visit' && <><p className="wizard-kicker">Начнём с главного</p><h1 id="wizard-question">Что хотите посетить?</h1><p className="wizard-subtitle">Выберите формат — остальные детали уточним дальше.</p>{discoveryError && <div className="notice notice--error">Не удалось загрузить типы мест. Можно пропустить вопрос и продолжить.</div>}{isLoadingTypes ? <p className="wizard-loading-copy">Загружаем варианты…</p> : <OptionStep selectedValue={state.draft.organization_type_id} options={types.map((type) => ({ value: type.id, label: type.name, hint: type.description || undefined, icon: typeIcons[type.code] }))} onSelect={(value) => answer('organization_type_id', String(value))} />}</>}
        {step === 'budget' && <><p className="wizard-kicker">Планируем расходы</p><h1 id="wizard-question">Какой у вас бюджет?</h1><p className="wizard-subtitle">Укажите общую сумму на всю компанию.</p><NumberStep label="Общий бюджет" min={0} suffix="₽" quickValues={[1500, 3000, 5000, 10000]} initialValue={state.draft.budget} onSubmit={(value) => answer('budget', value)} /></>}
        {step === 'party' && <><p className="wizard-kicker">Уточним компанию</p><h1 id="wizard-question">Сколько вас будет?</h1><p className="wizard-subtitle">Это поможет правильно рассчитать итоговую сумму.</p><OptionStep selectedValue={state.draft.party_size} options={[1, 2, 3, 4, 5, 6].map((value) => ({ value, label: String(value), hint: value === 1 ? 'человек' : value < 5 ? 'человека' : 'человек', icon: '•' }))} onSelect={(value) => answer('party_size', Number(value))} /></>}
        {step === 'city' && <><p className="wizard-kicker">Где будем искать</p><h1 id="wizard-question">В каком городе?</h1><p className="wizard-subtitle">Можно написать город вручную.</p><TextStep label="Город" placeholder="Например, Астрахань" maxLength={120} suggestions={cities} initialValue={state.draft.city} onSubmit={(value) => answer('city', value)} /></>}
        {step === 'wishes' && <><p className="wizard-kicker">Последний штрих</p><h1 id="wizard-question">Есть ещё пожелания?</h1><p className="wizard-subtitle">Например: тихий зал, вегетарианское меню или место для детей.</p><TextStep label="Ваши пожелания" placeholder="Опишите, что для вас важно…" multiline maxLength={500} submitLabel="Показать варианты" initialValue={state.draft.wishes} onSubmit={(value) => answer('wishes', value)} /></>}
      </div>

      <footer className="wizard-footer">
        <button className="wizard-back" type="button" disabled={state.stepIndex === 0} onClick={() => dispatch({ type: 'back' })}>← Назад</button>
        <button className="wizard-skip" type="button" onClick={skip}>Пропустить</button>
      </footer>
    </section>
  )
}
