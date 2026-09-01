import { useState } from 'react'
import { Info } from 'lucide-react'

// Hand-rolled hover/click popover - this codebase has no shadcn/ui or
// Radix (verified: neither appears anywhere in package.json or src/),
// so every tooltip-ish affordance elsewhere is a plain title="" attribute
// or an inline hint paragraph. This is the same idea with a richer panel
// (label/description/range/requires) than a native title="" can show.
export default function InfoTooltip({ label, description, range, requires }) {
  const [open, setOpen] = useState(false)

  return (
    <span className="relative inline-flex">
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        onMouseEnter={() => setOpen(true)}
        onMouseLeave={() => setOpen(false)}
        className="text-gray-400 hover:text-indigo-600"
        aria-label={`About ${label}`}
      >
        <Info size={12} />
      </button>
      {open && (
        <div className="absolute left-1/2 top-full z-20 mt-1.5 w-56 -translate-x-1/2 rounded-md border border-gray-200 bg-white p-2.5 text-left text-xs text-gray-600 shadow-lg">
          <p className="mb-1 font-semibold text-gray-800">{label}</p>
          {description && <p className="mb-1">{description}</p>}
          {range && <p className="text-gray-400">Range: {range}</p>}
          {requires && <p className="text-gray-400">Requires: {requires}</p>}
        </div>
      )}
    </span>
  )
}
