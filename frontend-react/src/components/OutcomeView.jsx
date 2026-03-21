import { useState } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip,
  ResponsiveContainer, Cell,
} from 'recharts'
import clsx from 'clsx'

const PILLARS = [
  'Effectiveness',
  'Efficiency',
  'Adaptability and Learning',
  'Collaboration and Interaction',
  'Trust and Safety',
  'Robustness and Generalization',
]

function PillarTooltip({ active, payload }) {
  if (!active || !payload?.length) return null
  const d = payload[0]
  const val = d.value
  return (
    <div className="bg-white border border-gray-200 rounded shadow-sm text-xs p-2 max-w-xs">
      <p className="font-semibold text-gray-800 mb-0.5">{d.payload?.name}</p>
      <p className="text-gray-500">
        {val == null
          ? 'Data not available for this pilot type'
          : val.toFixed(3)}
      </p>
    </div>
  )
}

function PillarChart({ metrics }) {
  // metrics: { [name]: number | null | undefined }
  const data = Object.entries(metrics).map(([name, value]) => ({
    name,
    value: typeof value === 'number' ? value : null,
  }))

  if (!data.length) {
    return (
      <div className="text-sm text-gray-400 py-10 text-center">
        No metrics in this pillar for this configuration.
      </div>
    )
  }

  const maxVal = Math.max(...data.map(d => d.value ?? 0), 1)

  return (
    <ResponsiveContainer width="100%" height={Math.max(data.length * 40 + 40, 120)}>
      <BarChart
        data={data}
        layout="vertical"
        margin={{ top: 4, right: 60, bottom: 4, left: 8 }}
      >
        <XAxis type="number" domain={[0, maxVal * 1.15]} tick={{ fontSize: 10 }} />
        <YAxis
          type="category" dataKey="name" width={200}
          tick={{ fontSize: 11 }} tickLine={false} axisLine={false}
        />
        <Tooltip content={<PillarTooltip />} />
        <Bar dataKey="value" maxBarSize={22} radius={[0, 3, 3, 0]}>
          {data.map((d, i) => (
            <Cell key={i} fill={d.value == null ? '#e5e7eb' : '#6366f1'} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}

export default function OutcomeView({ results, selectedIdx }) {
  const [activePillar, setActivePillar] = useState(PILLARS[0])

  const result = results[selectedIdx]
  const byGroup = result?.aggregates?.by_group ?? {}

  return (
    <div className="flex gap-6">
      {/* Pillar sidebar */}
      <div className="w-56 flex-shrink-0">
        <p className="text-xs font-medium text-gray-400 uppercase tracking-wide mb-2 px-1">
          Pillars
        </p>
        <nav className="space-y-0.5">
          {PILLARS.map(pillar => {
            const metrics = byGroup[pillar] ?? {}
            const total = Object.keys(metrics).length
            const available = Object.values(metrics).filter(v => typeof v === 'number').length
            return (
              <button
                key={pillar}
                onClick={() => setActivePillar(pillar)}
                className={clsx(
                  'w-full text-left px-3 py-2.5 rounded-md text-sm transition-colors',
                  activePillar === pillar
                    ? 'bg-indigo-50 text-indigo-700 font-medium'
                    : 'text-gray-600 hover:bg-gray-100',
                )}
              >
                <span className="block truncate leading-tight">{pillar}</span>
                <span className="text-xs text-gray-400 font-normal">
                  {available}/{total} available
                </span>
              </button>
            )
          })}
        </nav>
      </div>

      {/* Chart area */}
      <div className="flex-1 bg-white rounded-lg border border-gray-200 p-5">
        <h3 className="text-sm font-semibold text-gray-700 mb-0.5">{activePillar}</h3>
        <p className="text-xs text-gray-400 mb-4">
          Gray bars indicate metrics not logged by this pilot type.
        </p>
        <PillarChart metrics={byGroup[activePillar] ?? {}} />
      </div>
    </div>
  )
}
