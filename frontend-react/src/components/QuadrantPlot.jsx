import {
  ScatterChart, Scatter, XAxis, YAxis, CartesianGrid,
  Tooltip, ReferenceLine, ReferenceArea, ResponsiveContainer, Legend,
} from 'recharts'

export const PALETTE = [
  '#6366f1', '#f59e0b', '#10b981', '#ef4444',
  '#8b5cf6', '#0ea5e9', '#f97316', '#84cc16',
]

const Q_LABEL = { fontSize: 10, fill: '#d1d5db', fontStyle: 'italic' }

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
  const xSpan = Math.max(Math.max(...xs) - Math.min(...xs), 0.1)
  const ySpan = Math.max(Math.max(...ys) - Math.min(...ys), 0.1)

  const xMin = Math.min(Math.min(...xs) - xSpan * 0.3, xRef - xSpan * 0.5)
  const xMax = Math.max(Math.max(...xs) + xSpan * 0.3, xRef + xSpan * 0.5)
  const yMin = Math.min(Math.min(...ys) - ySpan * 0.2, yRef - 0.15, 0)
  const yMax = Math.max(Math.max(...ys) + ySpan * 0.2, yRef + 0.15, 1)

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4">
      <p className="text-sm font-semibold text-gray-700 mb-2">{title}</p>
      <ResponsiveContainer width="100%" height={290}>
        <ScatterChart margin={{ top: 10, right: 20, bottom: 32, left: 10 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
          <XAxis
            type="number" dataKey="x" domain={[xMin, xMax]} tick={{ fontSize: 10 }}
            label={{ value: xLabel, position: 'insideBottom', offset: -10, style: { fontSize: 10, fill: '#9ca3af' } }}
          />
          <YAxis
            type="number" dataKey="y" domain={[yMin, yMax]} tick={{ fontSize: 10 }}
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
          <Legend iconSize={8} wrapperStyle={{ fontSize: 11, paddingTop: 4 }} />

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
