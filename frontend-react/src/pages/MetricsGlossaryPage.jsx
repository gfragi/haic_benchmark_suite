import clsx from 'clsx'

const PILLARS = [
  {
    name: 'Interaction Patterns',
    color: 'indigo',
    desc: 'Measures the dynamics of how often and how efficiently humans and AI interact.',
    metrics: [
      {
        key: 'F',
        full: 'Interaction Frequency',
        unit: 'events/min',
        range: '0+, typical 0–50',
        better: 'higher',
        desc: 'The average number of human-AI interactions per minute. Higher frequency generally indicates more active collaboration, but should be interpreted in the context of task complexity.',
      },
      {
        key: 'D',
        full: 'Average Action Duration',
        unit: 'seconds',
        range: '0+',
        better: 'lower',
        desc: 'The mean time taken per interaction event. Shorter durations suggest the AI is providing timely, usable responses. Very long durations may indicate confusion or poor AI performance.',
      },
    ],
  },
  {
    name: 'Cognitive Alignment',
    color: 'violet',
    desc: 'Captures the human cognitive experience and trust level during AI-assisted tasks.',
    metrics: [
      {
        key: 'HCL',
        full: 'Human Cognitive Load proxy',
        unit: '0–1',
        range: '0–1',
        better: 'higher',
        desc: 'A proxy for human cognitive load derived from behavioral signals. Higher values indicate the human was engaged without being overloaded. Values near 0 suggest the human was overwhelmed or disengaged.',
      },
      {
        key: 'Tr',
        full: 'Trust proxy',
        unit: '0–1',
        range: '0–1',
        better: 'higher',
        desc: 'Measured by how often humans accept AI suggestions without overriding them. A high trust proxy indicates the human found AI outputs reliable. Low trust may reflect poor AI quality or miscalibration.',
      },
    ],
  },
  {
    name: 'Collaboration Dynamics',
    color: 'amber',
    desc: 'Evaluates how the collaboration evolves over time and how accurately synthetic agents replicate real behavior.',
    metrics: [
      {
        key: 'A',
        full: 'Adaptability Δ',
        unit: '-1 to 1',
        range: '-1 to 1',
        better: 'positive',
        desc: 'The change in collaboration quality from the start to the end of the session. Positive values indicate the human-AI team improved over time (learning effect). Negative values suggest degradation.',
      },
      {
        key: 'S',
        full: 'Surrogate Similarity',
        unit: '0–1',
        range: '0–1',
        better: 'higher',
        desc: 'How closely simulated (surrogate) agents match real human behavioral patterns. High similarity validates that synthetic evaluation data is representative — critical for simulation-based benchmarking.',
      },
    ],
  },
  {
    name: 'Efficiency',
    color: 'emerald',
    desc: 'Quantifies how much overhead the AI introduces and the overall productivity of the collaboration.',
    metrics: [
      {
        key: 'EL',
        full: 'Effort Loss',
        unit: 'ratio',
        range: '0+, 0 = optimal',
        better: 'lower',
        desc: 'The ratio of additional effort incurred due to the AI compared to a baseline. A value of 0 means the AI added no overhead. Higher values indicate the AI slowed down or complicated the workflow.',
      },
      {
        key: 'EfficiencyScore',
        full: 'Efficiency Score',
        unit: '0–1',
        range: '0–1',
        better: 'higher',
        desc: 'A composite score combining speed and output quality of the human-AI team. Aggregates multiple efficiency signals into a single 0–1 number for quick comparison across configurations.',
      },
    ],
  },
]

const DOMAIN_TABLE = [
  { domain: 'Healthcare', Tr: '0.80–0.95', HCL: '0.60–0.80', EL: '0.05–0.20' },
  { domain: 'Energy',     Tr: '0.70–0.85', HCL: '0.50–0.70', EL: '0.10–0.30' },
  { domain: 'Applications', Tr: '0.65–0.80', HCL: '0.55–0.75', EL: '0.15–0.40' },
]

const C = {
  indigo:  { border: 'border-indigo-200',  bg: 'bg-indigo-50',  text: 'text-indigo-700',  badge: 'bg-indigo-100 text-indigo-700'  },
  violet:  { border: 'border-violet-200',  bg: 'bg-violet-50',  text: 'text-violet-700',  badge: 'bg-violet-100 text-violet-700'  },
  amber:   { border: 'border-amber-200',   bg: 'bg-amber-50',   text: 'text-amber-700',   badge: 'bg-amber-100 text-amber-700'   },
  emerald: { border: 'border-emerald-200', bg: 'bg-emerald-50', text: 'text-emerald-700', badge: 'bg-emerald-100 text-emerald-700' },
}

export default function MetricsGlossaryPage() {
  return (
    <div className="space-y-8 max-w-3xl">

      <div>
        <h1 className="text-xl font-semibold text-gray-900">Metrics Reference</h1>
        <p className="mt-1 text-sm text-gray-500 leading-relaxed">
          The HAIC benchmark uses 8 core metrics organized into 4 pillars.
          Each metric captures a distinct dimension of human-AI collaboration quality.
          Together they produce a holistic picture of how effectively humans and AI systems work together.
        </p>
      </div>

      {PILLARS.map(pillar => {
        const c = C[pillar.color]
        return (
          <section key={pillar.name}>
            <div className={clsx('rounded-lg border p-4 mb-3', c.border, c.bg)}>
              <h2 className={clsx('text-sm font-semibold', c.text)}>{pillar.name}</h2>
              <p className="text-xs text-gray-600 mt-0.5">{pillar.desc}</p>
            </div>
            <div className="space-y-3">
              {pillar.metrics.map(m => (
                <div key={m.key} className="bg-white rounded-lg border border-gray-200 p-4">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex items-center gap-2">
                      <span className={clsx('px-2 py-0.5 rounded text-xs font-mono font-bold', c.badge)}>
                        {m.key}
                      </span>
                      <span className="text-sm font-medium text-gray-800">{m.full}</span>
                    </div>
                    <div className="text-right flex-shrink-0">
                      <p className="text-xs text-gray-400 font-mono">{m.unit}</p>
                      <p className="text-xs text-gray-400">better: {m.better}</p>
                    </div>
                  </div>
                  <p className="text-sm text-gray-600 mt-2 leading-relaxed">{m.desc}</p>
                  <p className="text-xs text-gray-400 mt-1.5">
                    <span className="font-medium">Range:</span> {m.range}
                  </p>
                </div>
              ))}
            </div>
          </section>
        )
      })}

      {/* Domain benchmarks */}
      <section>
        <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">
          Domain Benchmark Ranges
        </h2>
        <p className="text-xs text-gray-500 mb-3">
          Reference ranges for Tr, HCL, and EL based on domain-specific calibration. Values within
          these ranges indicate typical performance. These are used to contextualize metric cards in
          the results dashboard.
        </p>
        <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="text-left px-4 py-2.5 text-xs font-semibold text-gray-500">Domain</th>
                <th className="text-center px-4 py-2.5 text-xs font-semibold text-gray-500">Tr (Trust)</th>
                <th className="text-center px-4 py-2.5 text-xs font-semibold text-gray-500">HCL (Cognitive Load)</th>
                <th className="text-center px-4 py-2.5 text-xs font-semibold text-gray-500">EL (Effort Loss)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {DOMAIN_TABLE.map(row => (
                <tr key={row.domain} className="hover:bg-gray-50">
                  <td className="px-4 py-2.5 text-sm font-medium text-gray-700">{row.domain}</td>
                  <td className="px-4 py-2.5 text-center font-mono text-xs text-gray-600">{row.Tr}</td>
                  <td className="px-4 py-2.5 text-center font-mono text-xs text-gray-600">{row.HCL}</td>
                  <td className="px-4 py-2.5 text-center font-mono text-xs text-gray-600">{row.EL}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="text-xs text-gray-400 mt-2">
          Domain is auto-detected from the application name and description in your configuration.
        </p>
      </section>

    </div>
  )
}
