import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { SearchWizard } from './SearchWizard'

const types = [
  { id: 'restaurant-id', code: 'restaurant', name: 'Ресторан', description: null },
  { id: 'theater-id', code: 'theater', name: 'Театр', description: null },
]

describe('SearchWizard', () => {
  it('starts with the visit question and advances after an answer', async () => {
    render(<SearchWizard types={types} cities={['Астрахань']} onComplete={vi.fn()} />)

    expect(screen.getByRole('heading', { name: 'Что хотите посетить?' })).toBeVisible()
    await userEvent.click(screen.getByRole('button', { name: /Ресторан/ }))
    expect(screen.getByRole('heading', { name: 'Какой у вас бюджет?' })).toBeVisible()
    expect(screen.getByText('2 из 5')).toBeVisible()
  })

  it('submits an empty filter only once when skip-all is pressed repeatedly', async () => {
    let resolveSubmit: (() => void) | undefined
    const onComplete = vi.fn(
      () => new Promise<void>((resolve) => { resolveSubmit = resolve }),
    )
    render(<SearchWizard types={types} cities={[]} onComplete={onComplete} />)
    const skipAll = screen.getByRole('button', { name: 'Пропустить всё' })

    await userEvent.dblClick(skipAll)

    expect(onComplete).toHaveBeenCalledTimes(1)
    expect(onComplete).toHaveBeenCalledWith({})
    expect(screen.getByText('Подбираем варианты…')).toBeVisible()
    resolveSubmit?.()
  })

  it('keeps answers available when submission fails and can retry', async () => {
    const onComplete = vi
      .fn()
      .mockRejectedValueOnce(new Error('Сервис временно недоступен'))
      .mockResolvedValueOnce(undefined)
    render(<SearchWizard types={types} cities={[]} onComplete={onComplete} />)

    await userEvent.click(screen.getByRole('button', { name: /Театр/ }))
    await userEvent.click(screen.getByRole('button', { name: 'Пропустить' }))
    await userEvent.click(screen.getByRole('button', { name: 'Пропустить' }))
    await userEvent.click(screen.getByRole('button', { name: 'Пропустить' }))
    await userEvent.type(screen.getByLabelText('Ваши пожелания'), 'Хочу тихий зал')
    await userEvent.click(screen.getByRole('button', { name: /Показать варианты/ }))

    expect(await screen.findByText('Сервис временно недоступен')).toBeVisible()
    await userEvent.click(screen.getByRole('button', { name: 'Попробовать ещё раз' }))
    expect(onComplete).toHaveBeenLastCalledWith({
      organization_type_id: 'theater-id',
      wishes: 'Хочу тихий зал',
    })
  })

  it('restores a budget when navigating back so it can be edited', async () => {
    render(<SearchWizard types={types} cities={[]} onComplete={vi.fn()} />)
    await userEvent.click(screen.getByRole('button', { name: /Ресторан/ }))
    await userEvent.click(screen.getByRole('button', { name: /3.000 ₽/ }))
    await userEvent.click(screen.getByRole('button', { name: /Продолжить/ }))
    expect(screen.getByRole('heading', { name: 'Сколько вас будет?' })).toBeVisible()

    await userEvent.click(screen.getByRole('button', { name: /Назад/ }))

    expect(screen.getByRole('spinbutton', { name: 'Общий бюджет' })).toHaveValue(3000)
  })
})
