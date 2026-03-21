import clsx from 'clsx'
import { AlertTriangle } from 'lucide-react'

const METRICS = {
  F: {
    full: 'Interaction Frequency', unit: 'events/min',
    range: '0+, typical 0–50', better: 'higher',
    partner: 'How actively humans and AI interacted',
  },
  D: {
    full: 'Avg. Action Duration', unit: 'seconds',
    range: '0+', better: 'lower',
    partner: 'How long each interaction took on average',
  },
  HCL: {
    full: 'Human Cognitive Load proxy', unit: '0–1',
    range: '0–1', better: 'higher',
    partner: 'How much mental effort the human spent (lower = more overloaded)',
  },
  Tr: {
    full: 'Trust proxy', unit: '0–1',
    range: '0–1', better: 'higher',
    partner: 'How often humans accepted AI suggestions without overriding',
  },
  A: {
    full: 'Adaptability Δ', unit: '-1 to 1',
    range: '-1 to 1', better: 'positive',
    partner: 'Whether collaboration improved over the session',
  },
  S: {
    full: 'Surrogate Similarity', unit: '0–1',
    range: '0–1', better: 'higher',
    partner: 'How closely simulated agents matched real human behavior',
  },
  EL: {
    full: 'Effort Loss', unit: 'ratio',
    range: '0+, 0=optimal', better: 'lower',
    partner: 'How much slower the collaboration was vs. the baseline',
  },
  EfficiencyScore: {
    full: 'Efficiency Score', unit: '0–1',
    range: '0–1', better: 'higher',
    partner: 'Overall efficiency combining speed and quality',
  },
}

// Only Tr, HCL, EL have domain benchmarks
const DOMAIN_RANGES = {
  healthcare:   { Tr: [0.80, 0.95], HCL: [0.60, 0.80], EL: [0.05, 0.20] },
  energy:       { Tr: [0.70, 0.85], HCL: [0.50, 0.70], EL: [0.10, 0.30] },
  applications: { Tr: [0.65, 0.80], HCL: [0.55, 0.75], EL: [0.15, 0.40] },
}
const RANGE_METRICS = new Set(['Tr', 'HCL', 'EL'])

function colorFor(key, v) {
  if (v == null) return 'none'
  switch (key) {
    case 'Tr':             return v >= 0.7 ? 'green' : v >= 0.4 ? 'amber' : 'red'
    case 'HCL':            return v >= 0.6 ? 'green' : v >= 0.3 ? 'amber' : 'red'
    case 'EL':             return v <= 0.2 ? 'green' : v <= 0.5 ? 'amber' : 'red'
    case 'EfficiencyScore': return v >= 0.7 ? 'green' : v >= 0.4 ? 'amber' : 'red'
    case 'A':              return v > 0.1  ? 'green' : v >= -0.1 ? 'amber' : 'red'
    default:               return 'neutral'
  }
}

const STRIP = {
  green:   'bg-green-500',
  amber:   'bg-amber-400',
  red:     'bg-red-500',
  neutral: 'bg-gray-200',
  none:    'bg-gray-100',
}
const DOT = {
  green:   'bg-green-500',
  amber:   'bg-amber-400',
  red:     'bg-red-500',
  neutral: 'bg-gray-300',
  none:    'bg-gray-200',
}

function DomainRange({ metricKey, domain }) {
  if (!RANGE_METRICS.has(metricKey)) return null
  const domainRanges = DOMAIN_RANGES[domain?.toLowerCase()]
  if (!domainRanges) {
    return (
      <p className="text-xs text-gray-400 mt-1 italic">no reference range available</p>
    )
  }
  const range = domainRanges[metricKey]
  if (!range) return null
  return (
    <p className="text-xs text-gray-400 mt-1">
      Typical for <span className="font-medium capitalize">{domain}</span>:{' '}
      <span className="font-mono">{range[0].toFixed(2)}–{range[1].toFixed(2)}</span>
    </p>
  )
}

function WarningBox({ warnings, metricKey }) {
  if (!warnings?.length) return null
  return (
    <div className="mt-2 space-y-1">
      {warnings.map((w, i) => (
        <div
          key={i}
          className="flex items-start gap-1.5 rounded bg-amber-50 border border-amber-200 px-2 py-1.5 text-xs text-amber-700 leading-tight"
        >
          <AlertTriangle size={11} className="mt-0.5 flex-shrink-0" />
          <span>
            <span className="font-semibold">{metricKey}</span>
            {' — '}
            {w.warning}
          </span>
        </div>
      ))}
    </div>
  )
}

export default function MetricCard({ metricKey, value, audience, domain, warnings = [] }) {
  const meta = METRICS[metricKey]
  if (!meta) return null

  const color = colorFor(metricKey, value)
  const isNone = value == null
  const relevant = warnings.filter(w => w.metric === metricKey)

  return (
    <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
      <div className={clsx('h-1 w-full', STRIP[color])} />

      <div className="p-4">
        <div className="flex items-start justify-between gap-2">
          <div className="min-w-0">
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide truncate">
              {metricKey}
            </p>
            <p className="text-xs text-gray-400 mt-0.5 truncate">{meta.full}</p>
          </div>
          {audience === 'partner' && (
            <span className={clsx('w-3 h-3 rounded-full flex-shrink-0 mt-0.5', DOT[color])} />
          )}
        </div>

        {audience === 'researcher' ? (
          <>
            <p className={clsx(
              'text-2xl font-semibold mt-2 tabular-nums',
              isNone ? 'text-gray-300' : 'text-gray-900',
            )}>
              {isNone ? '—' : value.toFixed(3)}
            </p>
            <p className="text-xs text-gray-400 mt-0.5">
              {meta.unit} · {meta.range} · better: {meta.better}
            </p>
            <DomainRange metricKey={metricKey} domain={domain} />
            <WarningBox warnings={relevant} metricKey={metricKey} />
          </>
        ) : (
          <>
            <p className={clsx(
              'text-sm mt-2 leading-snug',
              isNone ? 'text-gray-300 italic' : 'text-gray-700',
            )}>
              {isNone ? 'Data not available' : meta.partner}
            </p>
            <DomainRange metricKey={metricKey} domain={domain} />
            <WarningBox warnings={relevant} metricKey={metricKey} />
          </>
        )}
      </div>
    </div>
  )
}
