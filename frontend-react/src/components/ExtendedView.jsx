import { useState } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, Legend,
  ResponsiveContainer,
} from 'recharts'
import clsx from 'clsx'
import { PALETTE } from './QuadrantPlot'

const PILLARS = [
  'Effectiveness',
  'Efficiency',
  'Adaptability and Learning',
  'Collaboration and Interaction',
  'Trust and Safety',
  'Robustness and Generalization',
]

function PillarTooltip({ active, payload, series }) {
  if (!active || !payload?.length) return null
  const name = payload[0]?.payload?.name
  return (
    <div className="bg-white border border-gray-200 rounded shadow-sm text-xs p-2 max-w-xs space-y-0.5">
      <p className="font-semibold text-gray-800 mb-0.5">{name}</p>
      {series.map(s => {
        const val = payload[0]?.payload?.[s.version]
        return (
          <p key={s.version} className="text-gray-500 flex items-center gap-1.5">
            <span className="inline-block w-2 h-2 rounded-full" style={{ backgroundColor: s.color }} />
            {s.version}: <span className="font-mono">{typeof val === 'number' ? val.toFixed(3) : 'n/a'}</span>
          </p>
        )
      })}
    </div>
  )
}

function PillarChart({ metricNames, series }) {
  // series: [{ version, color, values: { [metricName]: number | null } }]
  if (!metricNames.length) {
    return (
      <div className="text-sm text-gray-400 py-10 text-center">
        No metrics in this pillar for this configuration.
      </div>
    )
  }

  const data = metricNames.map(name => {
    const row = { name }
    series.forEach(s => {
      const v = s.values[name]
      row[s.version] = typeof v === 'number' ? v : null
    })
    return row
  })

  const maxVal = Math.max(
    ...data.flatMap(row => series.map(s => row[s.version] ?? 0)),
    1,
  )
  const barSize = series.length > 2 ? 14 : 20

  return (
    <ResponsiveContainer width="100%" height={Math.max(metricNames.length * 46 + 40, 140)}>
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
        <Tooltip content={(props) => <PillarTooltip {...props} series={series} />} />
        {series.length > 1 && <Legend wrapperStyle={{ fontSize: 11 }} />}
        {series.map(s => (
          <Bar key={s.version} dataKey={s.version} name={s.version} fill={s.color} maxBarSize={barSize} radius={[0, 3, 3, 0]} />
        ))}
      </BarChart>
    </ResponsiveContainer>
  )
}

export default function ExtendedView({ results }) {
  const [activePillar, setActivePillar] = useState(PILLARS[0])

  const series = results.map((r, i) => ({
    version: r.ai_model_version,
    color: PALETTE[i % PALETTE.length],
    values: r.aggregates?.by_group?.[activePillar] ?? {},
  }))
  const metricNames = [...new Set(series.flatMap(s => Object.keys(s.values)))]

  // Availability hint in the sidebar uses the union of metrics across all
  // currently-shown versions, not just one - a metric counts as "available"
  // if any selected version has it.
  const availabilityByPillar = PILLARS.reduce((acc, pillar) => {
    const allValues = results.map(r => r.aggregates?.by_group?.[pillar] ?? {})
    const names = new Set(allValues.flatMap(v => Object.keys(v)))
    const available = [...names].filter(n => allValues.some(v => typeof v[n] === 'number')).length
    acc[pillar] = { total: names.size, available }
    return acc
  }, {})

  return (
    <div className="flex gap-6">
      {/* Pillar sidebar */}
      <div className="w-56 flex-shrink-0">
        <p className="text-xs font-medium text-gray-400 uppercase tracking-wide mb-2 px-1">
          Pillars
        </p>
        <nav className="space-y-0.5">
          {PILLARS.map(pillar => {
            const { total, available } = availabilityByPillar[pillar]
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
          Missing bars indicate metrics not logged by this pilot type for that version.
        </p>
        <PillarChart metricNames={metricNames} series={series} />
      </div>
    </div>
  )
}
