import { useState, useRef, useEffect, useCallback } from 'react'
import { useQuery, useQueries } from '@tanstack/react-query'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Legend, LabelList, Cell,
} from 'recharts'
import { ChevronDown, X, ArrowRight, Loader2, Info } from 'lucide-react'
import clsx from 'clsx'
import { api } from '../services/api'

// ── Constants ────────────────────────────────────────────────

const PALETTE = [
  '#6366f1', '#f59e0b', '#10b981', '#ef4444',
  '#8b5cf6', '#0ea5e9', '#f97316', '#84cc16',
]

const CORE_METRICS = ['F', 'D', 'HCL', 'Tr', 'A', 'S', 'EL', 'EfficiencyScore']

const LOWER_BETTER = new Set(['EL', 'D'])

const STATUS_DOT = {
  completed: 'bg-green-500',
  running:   'bg-blue-400',
  failed:    'bg-red-400',
  pending:   'bg-gray-300',
}

// ── Helpers ──────────────────────────────────────────────────

function isRegression(metric, current, prev) {
  if (current == null || prev == null) return false
  return LOWER_BETTER.has(metric) ? current > prev : current < prev
}

function useClickOutside(ref, handler) {
  useEffect(() => {
    function onDown(e) {
      if (!ref.current || ref.current.contains(e.target)) return
      handler()
    }
    document.addEventListener('mousedown', onDown)
    return () => document.removeEventListener('mousedown', onDown)
  }, [ref, handler])
}

// ── Config multi-select dropdown ─────────────────────────────

function ConfigPicker({ configs, selectedIds, onToggle }) {
  const [open, setOpen] = useState(false)
  const ref = useRef(null)
  useClickOutside(ref, useCallback(() => setOpen(false), []))

  return (
    <div ref={ref} className="relative">
      <button
        onClick={() => setOpen(o => !o)}
        className={clsx(
          'flex items-center gap-2 px-3 py-2 bg-white border rounded-lg text-sm transition-colors',
          'min-w-[220px] justify-between',
          open
            ? 'border-indigo-400 ring-2 ring-indigo-100'
            : 'border-gray-200 hover:border-gray-300',
        )}
      >
        <span className={selectedIds.length === 0 ? 'text-gray-400' : 'text-gray-700'}>
          {selectedIds.length === 0
            ? 'Select configurations…'
            : `${selectedIds.length} selected`}
        </span>
        <ChevronDown
          size={14}
          className={clsx('text-gray-400 transition-transform duration-150', open && 'rotate-180')}
        />
      </button>

      {open && (
        <div className="absolute z-20 mt-1 left-0 bg-white border border-gray-200 rounded-lg shadow-lg w-80 max-h-72 overflow-y-auto">
          {configs.length === 0 && (
            <p className="px-4 py-3 text-sm text-gray-400">No configurations found.</p>
          )}
          {configs.map(cfg => {
            const order = selectedIds.indexOf(cfg.id)
            const checked = order !== -1
            return (
              <label
                key={cfg.id}
                className="flex items-start gap-3 px-4 py-2.5 hover:bg-gray-50 cursor-pointer select-none"
              >
                <input
                  type="checkbox"
                  checked={checked}
                  onChange={() => onToggle(cfg.id)}
                  className="mt-0.5 accent-indigo-600"
                />
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-1.5">
                    <span
                      className={clsx(
                        'w-1.5 h-1.5 rounded-full flex-shrink-0',
                        STATUS_DOT[cfg.evaluation_status] ?? STATUS_DOT.pending,
                      )}
                    />
                    <p className="text-sm font-medium text-gray-800 truncate">
                      {cfg.application_name}
                    </p>
                  </div>
                  <p className="text-xs text-gray-400 ml-3 truncate">{cfg.ai_model_name}</p>
                </div>
                {checked && (
                  <span
                    className="text-xs font-bold flex-shrink-0 mt-0.5"
                    style={{ color: PALETTE[order % PALETTE.length] }}
                  >
                    #{order + 1}
                  </span>
                )}
              </label>
            )
          })}
        </div>
      )}
    </div>
  )
}

// ── Ordered selection chips ───────────────────────────────────

function SelectionChips({ selectedIds, configs, stubQueries, latestStubs, onRemove }) {
  if (!selectedIds.length) return null
  return (
    <div className="flex items-center gap-2 flex-wrap">
      {selectedIds.map((id, i) => {
        const cfg = configs?.find(c => c.id === id)
        const noResults = stubQueries[i]?.isFetched && latestStubs[i] == null
        return (
          <span
            key={id}
            className={clsx(
              'inline-flex items-center gap-1.5 pl-2.5 pr-1.5 py-1 rounded-full text-xs font-medium border',
              noResults && 'opacity-60',
            )}
            style={{
              borderColor: PALETTE[i % PALETTE.length],
              color: PALETTE[i % PALETTE.length],
              backgroundColor: PALETTE[i % PALETTE.length] + '18',
            }}
          >
            <span className="font-bold">#{i + 1}</span>
            <span className="max-w-[120px] truncate">
              {cfg?.application_name ?? `Config ${id}`}
            </span>
            {noResults && (
              <span className="text-amber-500 text-[9px] font-normal">no results</span>
            )}
            <button
              onClick={() => onRemove(id)}
              className="ml-0.5 p-0.5 hover:opacity-70 rounded-full"
            >
              <X size={9} />
            </button>
          </span>
        )
      })}
      {selectedIds.length >= 2 && (
        <span className="flex items-center gap-1 text-xs text-gray-400">
          <ArrowRight size={10} />
          δ left → right
        </span>
      )}
    </div>
  )
}

// ── Delta label rendered inside each Bar ─────────────────────
// Returns a recharts LabelList content function (called per data point).

function makeDeltaLabel(configIdx, chartData) {
  return function DeltaLabel({ x, y, width, height, index }) {
    const row = chartData[index]
    if (!row) return null
    const delta = row[`d${configIdx}`]
    if (delta == null) return null
    const isReg = row[`r${configIdx}`]
    const sign = delta > 0 ? '+' : ''
    // Place above bar (height > 0) or above zero line (height < 0)
    const labelY = height >= 0 ? y - 4 : y + height - 4
    return (
      <text
        x={x + width / 2}
        y={labelY}
        textAnchor="middle"
        fontSize={8}
        fontWeight="600"
        fill={isReg ? '#d97706' : '#9ca3af'}
      >
        {sign}{delta.toFixed(2)}
      </text>
    )
  }
}

// ── Tooltip ───────────────────────────────────────────────────

function CompareTooltip({ active, payload, label, chartData, configs, selectedIds }) {
  if (!active || !payload?.length) return null
  const metricIdx = CORE_METRICS.indexOf(label)
  const row = chartData[metricIdx] ?? {}
  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-sm p-3 text-xs min-w-[190px]">
      <p className="font-semibold text-gray-800 mb-2">{label}</p>
      {payload.map(p => {
        // dataKey is 'v0', 'v1', etc.
        const i = parseInt(p.dataKey?.slice(1) ?? '0')
        const delta = row[`d${i}`]
        const isReg = row[`r${i}`]
        const cfg = configs?.find(c => c.id === selectedIds[i])
        return (
          <div key={p.dataKey} className="flex items-center gap-3 py-0.5">
            <span
              className="font-medium truncate max-w-[100px]"
              style={{ color: isReg ? '#f59e0b' : p.fill }}
            >
              {cfg?.application_name ?? p.name}
            </span>
            <span className="font-mono text-gray-700 ml-auto">
              {p.value?.toFixed(3) ?? '—'}
            </span>
            {delta != null && (
              <span
                className={clsx(
                  'font-mono',
                  isReg
                    ? 'text-amber-600'
                    : delta > 0
                    ? 'text-green-600'
                    : 'text-gray-400',
                )}
              >
                {delta > 0 ? '+' : ''}{delta.toFixed(3)}
              </span>
            )}
          </div>
        )
      })}
    </div>
  )
}

// ── Main page ─────────────────────────────────────────────────

export default function CompareVersionsPage() {
  const [selectedIds, setSelectedIds] = useState([])

  const toggle = useCallback((id) => {
    setSelectedIds(prev =>
      prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id],
    )
  }, [])

  // All configs for the picker
  const { data: configs, isLoading: configsLoading } = useQuery({
    queryKey: ['configs'],
    queryFn: () => api.configs.list(),
  })

  // Result stub lists for each selected config
  const stubQueries = useQueries({
    queries: selectedIds.map(configId => ({
      queryKey: ['result-stubs', configId],
      queryFn: async () => {
        try {
          return await api.results.list(configId)
        } catch (e) {
          if (e.message?.includes('No results found')) return []
          throw e
        }
      },
    })),
  })

  // Pick the latest stub for each config (last entry = most recent)
  const latestStubs = selectedIds.map((configId, i) => {
    const stubs = stubQueries[i]?.data
    if (!stubs?.length) return null
    return { configId, stub: stubs[stubs.length - 1] }
  })

  // Fetch full MinIO result for each latest stub
  const detailQueries = useQueries({
    queries: latestStubs.map((entry, i) => ({
      queryKey: entry
        ? ['result-detail', entry.configId, entry.stub.id]
        : ['noop', selectedIds[i]],
      queryFn: entry ? () => api.results.get(entry.configId, entry.stub.id) : () => null,
      enabled: entry != null,
    })),
  })

  // Align results back to selectedIds order
  const selectedResults = latestStubs.map((entry, i) =>
    entry ? (detailQueries[i]?.data ?? null) : null,
  )

  const isLoadingAny =
    configsLoading ||
    stubQueries.some(q => q.isFetching) ||
    detailQueries.some(q => q.isFetching)

  // ── Build chart data ────────────────────────────────────────
  // chartData[j] = { metric, v0, v1, …, d1, d2, …, r1, r2, … }
  // v{i}   = value for selectedIds[i]
  // d{i}   = delta vs selectedIds[i-1]   (i > 0)
  // r{i}   = is regression vs previous?  (i > 0)

  const chartData = CORE_METRICS.map(metric => {
    const row = { metric }
    selectedIds.forEach((_, i) => {
      const result = selectedResults[i]
      const val = result?.aggregates?.interaction?.[metric] ?? null
      row[`v${i}`] = val
      if (i > 0) {
        const prev = selectedResults[i - 1]?.aggregates?.interaction?.[metric] ?? null
        row[`d${i}`] = val != null && prev != null ? val - prev : null
        row[`r${i}`] = isRegression(metric, val, prev)
      }
    })
    return row
  })

  const hasData = selectedIds.length > 0 && selectedResults.some(r => r != null)
  const ready   = !isLoadingAny && hasData

  // ── Render ──────────────────────────────────────────────────

  return (
    <div className="space-y-5">
      <h1 className="text-xl font-semibold text-gray-900">Compare Versions</h1>

      {/* Selector row */}
      <div className="flex items-start gap-4 flex-wrap">
        <ConfigPicker
          configs={configs ?? []}
          selectedIds={selectedIds}
          onToggle={toggle}
        />
        <SelectionChips
          selectedIds={selectedIds}
          configs={configs}
          stubQueries={stubQueries}
          latestStubs={latestStubs}
          onRemove={toggle}
        />
      </div>

      {/* ── Empty / hint states ── */}
      {selectedIds.length === 0 && (
        <div className="flex items-center justify-center gap-2 py-20 text-sm text-gray-400">
          <Info size={15} />
          Select 2 or more configurations to compare their core HAIC metrics.
        </div>
      )}

      {selectedIds.length === 1 && !isLoadingAny && (
        <div className="flex items-center gap-2 bg-gray-50 border border-gray-200 rounded-lg p-4 text-sm text-gray-500">
          <Info size={14} className="flex-shrink-0" />
          Select at least one more configuration to see deltas and regression highlights.
        </div>
      )}

      {/* ── Loading ── */}
      {isLoadingAny && selectedIds.length > 0 && (
        <div className="flex items-center justify-center gap-2 py-16 text-gray-400 text-sm">
          <Loader2 size={15} className="animate-spin" />
          Loading result data…
        </div>
      )}

      {/* ── Comparison chart ── */}
      {ready && (
        <div className="bg-white rounded-lg border border-gray-200 p-5">
          <div className="mb-4">
            <h2 className="text-sm font-semibold text-gray-700">Core HAIC Metrics</h2>
            <p className="text-xs text-gray-400 mt-0.5">
              Amber bars = regression vs preceding config.
              {selectedIds.length >= 2 && ' δ shown above each comparison bar.'}
              {' '}Values are raw (metrics have different scales).
            </p>
          </div>

          <ResponsiveContainer width="100%" height={340}>
            <BarChart
              data={chartData}
              barGap={3}
              barCategoryGap="22%"
              margin={{ top: 22, right: 20, bottom: 8, left: 10 }}
            >
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f3f4f6" />
              <XAxis dataKey="metric" tick={{ fontSize: 11 }} tickLine={false} />
              <YAxis tick={{ fontSize: 10 }} tickLine={false} axisLine={false} />
              <Tooltip
                content={(props) => (
                  <CompareTooltip
                    {...props}
                    chartData={chartData}
                    configs={configs}
                    selectedIds={selectedIds}
                  />
                )}
              />
              <Legend
                formatter={(value, entry) => {
                  const i = parseInt(entry.dataKey?.slice(1) ?? '0')
                  const cfg = configs?.find(c => c.id === selectedIds[i])
                  return (
                    <span style={{ fontSize: 11 }}>
                      #{i + 1} {cfg?.application_name ?? value}
                    </span>
                  )
                }}
              />

              {selectedIds.map((configId, i) => {
                const cfg = configs?.find(c => c.id === configId)
                return (
                  <Bar
                    key={configId}
                    dataKey={`v${i}`}
                    name={cfg?.application_name ?? `Config ${configId}`}
                    fill={PALETTE[i % PALETTE.length]}
                    maxBarSize={44}
                    radius={[3, 3, 0, 0]}
                  >
                    {/* Per-cell fill: amber if regression, palette color otherwise */}
                    {chartData.map((row, j) => (
                      <Cell
                        key={j}
                        fill={row[`r${i}`] ? '#fbbf24' : PALETTE[i % PALETTE.length]}
                      />
                    ))}
                    {/* Delta badges — only for configs after the first */}
                    {i > 0 && (
                      <LabelList
                        dataKey={`v${i}`}
                        content={makeDeltaLabel(i, chartData)}
                      />
                    )}
                  </Bar>
                )
              })}
            </BarChart>
          </ResponsiveContainer>

          {/* Legend row */}
          {selectedIds.length >= 2 && (
            <div className="flex items-center gap-5 mt-3 pt-3 border-t border-gray-100 flex-wrap">
              <div className="flex items-center gap-1.5 text-xs text-gray-500">
                <span className="w-3 h-3 rounded-sm bg-amber-400 inline-block flex-shrink-0" />
                Regression (worse than preceding config)
              </div>
              <div className="flex items-center gap-1.5 text-xs text-gray-500">
                <span className="font-mono font-bold text-amber-600 text-[11px]">δ</span>
                Delta shown above comparison bars
              </div>
              <div className="flex items-center gap-1.5 text-xs text-gray-500">
                <span className="font-mono text-green-600 text-[11px]">+0.xx</span>
                Improvement
              </div>
            </div>
          )}
        </div>
      )}

      {/* No-results state after loading */}
      {!isLoadingAny && selectedIds.length > 0 && !hasData && (
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-5 text-sm text-amber-700 text-center">
          None of the selected configurations have evaluation results yet.
        </div>
      )}
    </div>
  )
}
