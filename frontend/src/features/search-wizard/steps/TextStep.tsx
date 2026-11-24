import { useState, type FormEvent } from 'react'

interface TextStepProps {
  label: string
  placeholder: string
  multiline?: boolean
  maxLength: number
  suggestions?: string[]
  initialValue?: string
  submitLabel?: string
  onSubmit: (value: string) => void
}

export function TextStep({
  label,
  placeholder,
  multiline = false,
  maxLength,
  suggestions = [],
  initialValue = '',
  submitLabel = 'Продолжить',
  onSubmit,
}: TextStepProps) {
  const [value, setValue] = useState(initialValue)

  function submit(event: FormEvent) {
    event.preventDefault()
    const normalized = value.trim()
    if (normalized) onSubmit(normalized)
  }

  return (
    <form className="wizard-answer-form" onSubmit={submit}>
      <label className="wizard-field">
        <span className="sr-only">{label}</span>
        {multiline ? (
          <textarea
            aria-label={label}
            autoFocus
            maxLength={maxLength}
            placeholder={placeholder}
            rows={5}
            value={value}
            onChange={(event) => setValue(event.target.value)}
          />
        ) : (
          <input
            aria-label={label}
            autoFocus
            list="wizard-suggestions"
            maxLength={maxLength}
            placeholder={placeholder}
            value={value}
            onChange={(event) => setValue(event.target.value)}
          />
        )}
      </label>
      {suggestions.length > 0 && <datalist id="wizard-suggestions">{suggestions.map((item) => <option key={item} value={item} />)}</datalist>}
      {multiline && <small className="wizard-character-count">{value.length} / {maxLength}</small>}
      <button className="wizard-primary" disabled={!value.trim()} type="submit">{submitLabel}<span>→</span></button>
    </form>
  )
}
