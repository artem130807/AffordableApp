import type { OrganizationType } from './types'

export type View = 'discover' | 'places' | 'manage'

export const typeMeta: Record<string, { icon: string; color: string }> = {
  restaurant: { icon: '⌁', color: 'coral' },
  theater: { icon: '◐', color: 'violet' },
  electronics_store: { icon: '◇', color: 'blue' },
  entertainment: { icon: '✦', color: 'mint' },
}

export const formatMoney = (value: string | number) =>
  `${Number(value).toLocaleString('ru-RU', { maximumFractionDigits: 0 })} ₽`

export const findType = (typeId: string, types: OrganizationType[]) =>
  types.find((type) => type.id === typeId)
