interface Option {
  value: string | number
  label: string
  hint?: string
  icon?: string
}

interface OptionStepProps {
  options: Option[]
  selectedValue?: string | number
  onSelect: (value: string | number) => void
}

export function OptionStep({ options, selectedValue, onSelect }: OptionStepProps) {
  return (
    <div className="wizard-options">
      {options.map((option) => (
        <button
          aria-pressed={selectedValue === option.value}
          className={`wizard-option ${selectedValue === option.value ? 'selected' : ''}`}
          key={option.value}
          type="button"
          onClick={() => onSelect(option.value)}
        >
          <span className="wizard-option__icon" aria-hidden="true">{option.icon || '○'}</span>
          <span><strong>{option.label}</strong>{option.hint && <small>{option.hint}</small>}</span>
          <span className="wizard-option__arrow" aria-hidden="true">→</span>
        </button>
      ))}
    </div>
  )
}
