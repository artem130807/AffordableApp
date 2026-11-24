import { describe, expect, it } from 'vitest'
import { initialWizardState, wizardReducer, wizardSteps } from './wizardState'

describe('wizardReducer', () => {
  it('stores an answer immutably and advances to the next step', () => {
    const next = wizardReducer(initialWizardState, {
      type: 'answer',
      field: 'organization_type_id',
      value: 'restaurant-id',
    })

    expect(next.stepIndex).toBe(1)
    expect(next.draft.organization_type_id).toBe('restaurant-id')
    expect(initialWizardState.draft.organization_type_id).toBeUndefined()
  })

  it('skips only the current step and can navigate back', () => {
    const skipped = wizardReducer(initialWizardState, { type: 'skip' })
    const previous = wizardReducer(skipped, { type: 'back' })

    expect(skipped.stepIndex).toBe(1)
    expect(previous.stepIndex).toBe(0)
  })

  it('removes a previously answered value when that step is skipped', () => {
    let state = wizardReducer(initialWizardState, {
      type: 'answer',
      field: 'organization_type_id',
      value: 'restaurant-id',
    })
    state = wizardReducer(state, { type: 'answer', field: 'budget', value: 3000 })
    state = wizardReducer(state, { type: 'back' })

    const skipped = wizardReducer(state, { type: 'skip' })

    expect(skipped.stepIndex).toBe(2)
    expect(skipped.draft.budget).toBeUndefined()
    expect(skipped.draft.organization_type_id).toBe('restaurant-id')
  })

  it('marks skip-all as complete with an empty filter', () => {
    const completed = wizardReducer(initialWizardState, { type: 'skip_all' })

    expect(completed.isComplete).toBe(true)
    expect(completed.draft).toEqual({})
    expect(completed.stepIndex).toBe(wizardSteps.length - 1)
  })

  it('completes after answering the final question', () => {
    let state = initialWizardState
    for (let index = 0; index < wizardSteps.length - 1; index += 1) {
      state = wizardReducer(state, { type: 'skip' })
    }
    state = wizardReducer(state, { type: 'answer', field: 'wishes', value: 'тихо' })

    expect(state.isComplete).toBe(true)
    expect(state.draft.wishes).toBe('тихо')
  })
})
