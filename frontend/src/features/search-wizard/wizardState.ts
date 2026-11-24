import type { RecommendationFilterDraft } from '../../types'

export const wizardSteps = ['visit', 'budget', 'party', 'city', 'wishes'] as const
export const wizardFields: ReadonlyArray<DraftField> = [
  'organization_type_id',
  'budget',
  'party_size',
  'city',
  'wishes',
]

export interface WizardState {
  stepIndex: number
  draft: RecommendationFilterDraft
  isComplete: boolean
}

type DraftField = keyof RecommendationFilterDraft

export type WizardAction =
  | { type: 'answer'; field: DraftField; value: string | number }
  | { type: 'skip' }
  | { type: 'skip_all' }
  | { type: 'back' }
  | { type: 'reset' }

export const initialWizardState: WizardState = {
  stepIndex: 0,
  draft: {},
  isComplete: false,
}

export function wizardReducer(state: WizardState, action: WizardAction): WizardState {
  if (action.type === 'reset') return initialWizardState
  if (action.type === 'skip_all') {
    return { stepIndex: wizardSteps.length - 1, draft: {}, isComplete: true }
  }
  if (action.type === 'back') {
    return { ...state, stepIndex: Math.max(0, state.stepIndex - 1), isComplete: false }
  }

  const isLastStep = state.stepIndex === wizardSteps.length - 1
  if (action.type === 'skip') {
    const draft = { ...state.draft }
    delete draft[wizardFields[state.stepIndex]]
    return {
      stepIndex: isLastStep ? state.stepIndex : state.stepIndex + 1,
      draft,
      isComplete: isLastStep,
    }
  }

  return {
    stepIndex: isLastStep ? state.stepIndex : state.stepIndex + 1,
    draft: { ...state.draft, [action.field]: action.value },
    isComplete: isLastStep,
  }
}
