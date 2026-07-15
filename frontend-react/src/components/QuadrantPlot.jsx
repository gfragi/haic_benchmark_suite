import {
  ScatterChart, Scatter, XAxis, YAxis, CartesianGrid,
  Tooltip, ReferenceLine, ReferenceArea, ResponsiveContainer, Legend,
} from 'recharts'

export const PALETTE = [
  '#6366f1', '#f59e0b', '#10b981', '#ef4444',
  '#8b5cf6', '#0ea5e9', '#f97316', '#84cc16',
]

const Q_LABEL = { fontSize: 10, fill: '#d1d5db', fontStyle: 'italic' }

function median(values) {
  const sorted = [...values].sort((a, b) => a - b)
  const mid = Math.floor(sorted.length / 2)
  return sorted.length % 2 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2
}

// Robust axis bounds: uses median + median-absolute-deviation instead of raw
// min/max, so a single corrupted/outlier data point (e.g. a garbage value in
// test data) can't stretch the whole domain and squash every real point into
// one corner. Outliers beyond 6 MADs are excluded from the span calculation
// but still get plotted — they just render clipped at the axis edge.
function robustDomain(values, ref) {
  const all = [...values, ref]
  if (values.length < 3) {
    const min = Math.min(...all)
    const max = Math.max(...all)
    const span = Math.max(max - min, 0.1)
    return [min - span * 0.3, max + span * 0.3]
  }
  const med = median(values)
  const mad = median(values.map(v => Math.abs(v - med))) || 0.1
  const filtered = values.filter(v => Math.abs(v - med) <= mad * 6)
  const useValues = filtered.length >= 2 ? [...filtered, ref] : all
  const min = Math.min(...useValues)
  const max = Math.max(...useValues)
  const span = Math.max(max - min, 0.1)
  return [min - span * 0.3, max + span * 0.3]
}

function ScatterTooltip({ active, payload, xLabel, yLabel }) {
  if (!active || !payload?.length) return null
  const d = payload[0]?.payload
  if (!d) return null
  return (
    <div className="bg-white border border-gray-200 rounded shadow-sm text-xs p-2 space-y-0.5">
      <p className="font-semibold text-gray-800">{d.version}</p>
      <p className="text-gray-500">
        {xLabel}: <span className="font-mono">{d.x?.toFixed(3) ?? '—'}</span>
      </p>
      <p className="text-gray-500">
        {yLabel}: <span className="font-mono">{d.y?.toFixed(3) ?? '—'}</span>
      </p>
    </div>
  )
}

export default function QuadrantPlot({ title, points, xLabel, yLabel, xRef, yRef, quadrants }) {
  const valid = points.filter(p => p.x != null && p.y != null)

  if (!valid.length) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <p className="text-sm font-semibold text-gray-700 mb-3">{title}</p>
        <div className="flex items-center justify-center h-52 text-sm text-gray-300">
          No data available
        </div>
      </div>
    )
  }

  const xs = valid.map(p => p.x)
  const ys = valid.map(p => p.y)
  const [xMin, xMax] = robustDomain(xs, xRef)
  const [yMinRaw, yMaxRaw] = robustDomain(ys, yRef)
  const yMin = Math.min(yMinRaw, 0)
  const yMax = Math.max(yMaxRaw, 1)

  // One legend entry per unique version, even if several data points share it
  // (e.g. many test results with no real version tag) - otherwise the legend
  // repeats the same label once per point.
  const legendPayload = [...new Map(valid.map(p => [p.version, p])).values()]
    .map(p => ({ value: p.version, type: 'circle', color: p.color }))

  // Fixed 2-decimal ticks break down for metrics like F (interaction
  // frequency), which can be a tiny fraction of an event/minute - every tick
  // would round to "0.00", making the axis look empty even with real data.
  // Pick decimal places from the axis's own span instead of a flat count, so
  // ticks stay readable whether the metric ranges over 0-1 or 0-0.0005.
  function tickFormatterFor(min, max) {
    const span = Math.abs(max - min) || 1
    if (span < 0.001) return (v) => Number(v).toExponential(1)
    if (span < 0.01) return (v) => Number(v).toFixed(5)
    if (span < 0.1) return (v) => Number(v).toFixed(4)
    if (span < 1) return (v) => Number(v).toFixed(3)
    if (span < 10) return (v) => Number(v).toFixed(2)
    if (span < 1000) return (v) => Number(v).toFixed(1)
    return (v) => Number(v).toFixed(0)
  }
  const xTickFmt = tickFormatterFor(xMin, xMax)
  const yTickFmt = tickFormatterFor(yMin, yMax)

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4">
      <p className="text-sm font-semibold text-gray-700 mb-2">{title}</p>
      <ResponsiveContainer width="100%" height={290}>
        <ScatterChart margin={{ top: 10, right: 20, bottom: 32, left: 10 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
          <XAxis
            type="number" dataKey="x" domain={[xMin, xMax]} tick={{ fontSize: 10 }}
            tickFormatter={xTickFmt}
            label={{ value: xLabel, position: 'insideBottom', offset: -10, style: { fontSize: 10, fill: '#9ca3af' } }}
          />
          <YAxis
            type="number" dataKey="y" domain={[yMin, yMax]} tick={{ fontSize: 10 }}
            tickFormatter={yTickFmt}
            label={{ value: yLabel, angle: -90, position: 'insideLeft', offset: 10, style: { fontSize: 10, fill: '#9ca3af' } }}
          />

          {/* Quadrant backgrounds — transparent, labels only */}
          <ReferenceArea x1={xMin} x2={xRef} y1={yRef} y2={yMax}
            fill="none" stroke="none"
            label={{ value: quadrants.topLeft, position: 'center', style: Q_LABEL }} />
          <ReferenceArea x1={xRef} x2={xMax} y1={yRef} y2={yMax}
            fill="none" stroke="none"
            label={{ value: quadrants.topRight, position: 'center', style: Q_LABEL }} />
          <ReferenceArea x1={xMin} x2={xRef} y1={yMin} y2={yRef}
            fill="none" stroke="none"
            label={{ value: quadrants.bottomLeft, position: 'center', style: Q_LABEL }} />
          <ReferenceArea x1={xRef} x2={xMax} y1={yMin} y2={yRef}
            fill="none" stroke="none"
            label={{ value: quadrants.bottomRight, position: 'center', style: Q_LABEL }} />

          {/* Divider lines */}
          <ReferenceLine x={xRef} stroke="#e5e7eb" strokeDasharray="5 3" />
          <ReferenceLine y={yRef} stroke="#e5e7eb" strokeDasharray="5 3" />

          <Tooltip content={(props) => <ScatterTooltip {...props} xLabel={xLabel} yLabel={yLabel} />} />
          <Legend iconSize={8} wrapperStyle={{ fontSize: 11, paddingTop: 4 }} payload={legendPayload} />

          {valid.map((point, i) => (
            <Scatter
              key={`${i}-${point.version}`}
              name={point.version}
              fill={point.color}
              data={[{ x: point.x, y: point.y, version: point.version }]}
              size={100}
            />
          ))}
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  )
}
