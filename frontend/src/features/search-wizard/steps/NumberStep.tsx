import { useState, type FormEvent } from 'react'

interface NumberStepProps {
  label: string
  suffix?: string
  min: number
  max?: number
  quickValues?: number[]
  initialValue?: number
  submitLabel?: string
  onSubmit: (value: number) => void
}

export function NumberStep({
  label,
  suffix,
  min,
  max,
  quickValues = [],
  initialValue,
  submitLabel = 'Продолжить',
  onSubmit,
}: NumberStepProps) {
  const [value, setValue] = useState(initialValue === undefined ? '' : String(initialValue))

  function submit(event: FormEvent) {
    event.preventDefault()
    const parsed = Number(value)
    if (Number.isFinite(parsed) && parsed >= min && (max === undefined || parsed <= max)) {
      onSubmit(parsed)
    }
  }

  return (
    <form className="wizard-answer-form" onSubmit={submit}>
      <label className="wizard-field">
        <span className="sr-only">{label}</span>
        <div className="wizard-number-input">
          <input
            aria-label={label}
            inputMode="numeric"
            min={min}
            max={max}
            type="number"
            value={value}
            onChange={(event) => setValue(event.target.value)}
            autoFocus
          />
          {suffix && <span>{suffix}</span>}
        </div>
      </label>
      {quickValues.length > 0 && (
        <div className="wizard-quick-values">
          {quickValues.map((quickValue) => (
            <button key={quickValue} type="button" onClick={() => setValue(String(quickValue))}>
              {quickValue.toLocaleString('ru-RU')} {suffix}
            </button>
          ))}
        </div>
      )}
      <button className="wizard-primary" disabled={!value} type="submit">{submitLabel}<span>→</span></button>
    </form>
  )
}
