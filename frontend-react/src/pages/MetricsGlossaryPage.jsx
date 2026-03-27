import { useState } from 'react'
import clsx from 'clsx'

// ── Core HAIC ────────────────────────────────────────────────────────────────

const CORE_PILLARS = [
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
        desc: 'Average number of human-AI interactions per minute. Higher frequency indicates more active collaboration, but should be read in the context of task complexity.',
      },
      {
        key: 'D',
        full: 'Average Action Duration',
        unit: 'seconds',
        range: '0+',
        better: 'lower',
        desc: 'Mean time per interaction event. Shorter durations suggest the AI provides timely, usable responses. Very long durations may indicate confusion or poor AI performance.',
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
        desc: 'A proxy derived from behavioral signals. Higher values = engaged without being overloaded. Values near 0 suggest the human was overwhelmed or disengaged.',
      },
      {
        key: 'Tr',
        full: 'Trust proxy',
        unit: '0–1',
        range: '0–1',
        better: 'higher',
        desc: 'Fraction of AI suggestions accepted without override. High trust indicates reliable AI output. Low trust may reflect poor quality or miscalibration.',
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
        desc: 'Change in collaboration quality from start to end of session. Positive = learning effect. Negative = degradation.',
      },
      {
        key: 'S',
        full: 'Surrogate Similarity',
        unit: '0–1',
        range: '0–1',
        better: 'higher',
        desc: 'How closely simulated agents match real human behavioral patterns. Critical for validating simulation-based benchmarking.',
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
        desc: 'Ratio of additional effort from the AI vs baseline. 0 = no overhead. Higher = AI slowed or complicated the workflow.',
      },
      {
        key: 'EfficiencyScore',
        full: 'Efficiency Score',
        unit: '0–1',
        range: '0–1',
        better: 'higher',
        desc: 'Composite score combining speed and output quality. Aggregates multiple efficiency signals for quick cross-configuration comparison.',
      },
    ],
  },
]

const DOMAIN_TABLE = [
  { domain: 'Healthcare',   Tr: '0.80–0.95', HCL: '0.60–0.80', EL: '0.05–0.20' },
  { domain: 'Energy',       Tr: '0.70–0.85', HCL: '0.50–0.70', EL: '0.10–0.30' },
  { domain: 'Applications', Tr: '0.65–0.80', HCL: '0.55–0.75', EL: '0.15–0.40' },
]

// ── Extended Metrics ───────────────────────────────────────────────────────────

const EXTENDED_PILLARS = [
  {
    name: 'Effectiveness',
    color: 'indigo',
    desc: 'Classification and prediction quality of the AI model against ground-truth labels.',
    metrics: [
      {
        key: 'prediction_accuracy',
        full: 'Prediction Accuracy',
        unit: '0–1',
        better: 'higher',
        formula: '(TP + TN) / N',
        desc: 'Fraction of events where AI prediction matches ground truth.',
        fields: ['result_label  OR  prediction + ground_truth'],
      },
      {
        key: 'precision',
        full: 'Precision',
        unit: '0–1',
        better: 'higher',
        formula: 'TP / (TP + FP)',
        desc: 'Of all positive predictions, how many were actually positive.',
        fields: ['result_label  OR  prediction + ground_truth'],
      },
      {
        key: 'recall',
        full: 'Recall',
        unit: '0–1',
        better: 'higher',
        formula: 'TP / (TP + FN)',
        desc: 'Of all true positives, how many did the AI correctly flag.',
        fields: ['result_label  OR  prediction + ground_truth'],
      },
      {
        key: 'overall_system_accuracy',
        full: 'Overall System Accuracy',
        unit: '%',
        better: 'higher',
        formula: 'correct / total × 100',
        desc: 'Percentage of events where the human-AI team reached the correct outcome.',
        fields: ['correct / is_correct / agreement  OR  result ("correct"/"incorrect")'],
      },
      {
        key: 'model_improvement_rate',
        full: 'Model Improvement Rate',
        unit: 'Δ/interval',
        better: 'higher',
        formula: '(post_adaptation − pre_adaptation) / time_interval',
        desc: 'Rate at which AI performance improves across the session.',
        fields: ['post_adaptation_performance', 'pre_adaptation_performance', 'time_interval (optional)'],
      },
    ],
  },
  {
    name: 'Efficiency',
    color: 'emerald',
    desc: 'Time, resource, and error costs of the human-AI workflow.',
    metrics: [
      {
        key: 'response_time',
        full: 'Response Time',
        unit: 'seconds',
        better: 'lower',
        formula: 'mean(response_time_s)',
        desc: 'Average time the AI takes to respond to each human action.',
        fields: ['response_time / time_to_response / duration_s  OR  latency_ms'],
      },
      {
        key: 'teaching_efficiency',
        full: 'Teaching Efficiency',
        unit: 'gain/s',
        better: 'higher',
        formula: 'performance_improvement / time_spent',
        desc: 'Performance gain per unit of time invested in training or guiding the AI.',
        fields: ['performance_improvement / learning_gain', 'time_spent / learning_time'],
      },
      {
        key: 'query_efficiency',
        full: 'Query Efficiency',
        unit: 'ratio',
        better: 'lower',
        formula: 'total_queries / successful_hits',
        desc: 'Average number of queries required to reach a target — lower means more efficient retrieval.',
        fields: ['reached_target / meets_target / target_reached (bool)'],
      },
      {
        key: 'resource_utilization',
        full: 'Resource Utilization',
        unit: '%',
        better: 'contextual',
        formula: 'resources_used / total_resources × 100',
        desc: 'Proportion of available compute or memory resources consumed during the session.',
        fields: ['resources_used / cpu_used / gpu_used / mem_used', 'total_resources / cpu_total'],
      },
      {
        key: 'task_completion_time',
        full: 'Task Completion Time (Saved)',
        unit: 'seconds',
        better: 'higher',
        formula: 'time_without_ai − time_with_ai',
        desc: 'Time saved by using the AI. Positive values indicate the AI accelerated the task.',
        fields: ['time_without_ai', 'time_with_ai'],
      },
      {
        key: 'correction_efficiency',
        full: 'Correction Efficiency',
        unit: 'ratio',
        better: 'higher',
        formula: 'correction_effectiveness / correction_time',
        desc: 'Quality of corrections per unit of time spent correcting AI mistakes.',
        fields: ['correction_effectiveness', 'correction_time / time_spent_correcting'],
      },
      {
        key: 'error_reduction_rate',
        full: 'Error Reduction Rate',
        unit: '%',
        better: 'higher',
        formula: '(errors_before − errors_after) / errors_before × 100',
        desc: 'Percentage reduction in errors from the start to end of the collaboration session.',
        fields: ['errors_before', 'errors_after'],
      },
      {
        key: 'knowledge_retention',
        full: 'Knowledge Retention',
        unit: '%',
        better: 'higher',
        formula: 'post_retention / pre_retention × 100',
        desc: 'Ratio of post-session to pre-session performance — measures how much was retained.',
        fields: ['pre_retention_performance', 'post_retention_performance'],
      },
    ],
  },
  {
    name: 'Adaptability and Learning',
    color: 'violet',
    desc: 'How well the human-AI team learns, adapts, and responds to corrections over time.',
    metrics: [
      {
        key: 'feedback_impact',
        full: 'Feedback Impact',
        unit: 'Δ score',
        better: 'higher',
        formula: 'post_feedback − pre_feedback',
        desc: 'Performance improvement attributable to feedback given to the AI.',
        fields: ['pre_feedback_performance', 'post_feedback_performance'],
      },
      {
        key: 'adaptability_score',
        full: 'Adaptability Score',
        unit: 'Δ score',
        better: 'higher',
        formula: 'post_adaptation − pre_adaptation',
        desc: 'Overall performance change after adaptation to a new task or domain.',
        fields: ['pre_adaptation_performance', 'post_adaptation_performance'],
      },
      {
        key: 'impact_of_corrections',
        full: 'Impact of Corrections',
        unit: 'Δ score',
        better: 'higher',
        formula: 'post_correction − pre_correction',
        desc: 'Performance change after human corrections are applied to the AI.',
        fields: ['pre_correction_performance', 'post_correction_performance'],
      },
      {
        key: 'learning_efficiency',
        full: 'Learning Efficiency',
        unit: 'gain/s',
        better: 'higher',
        formula: 'performance_improvement / time_spent',
        desc: 'Rate of performance gain per unit of learning time.',
        fields: ['performance_improvement / learning_gain', 'time_spent / total_time'],
      },
      {
        key: 'objective_fulfillment_rate',
        full: 'Objective Fulfillment Rate',
        unit: '0–1',
        better: 'higher',
        formula: 'achieved / total',
        desc: 'Fraction of objectives successfully completed during the session.',
        fields: ['ground_truth = "achieved"  OR  objective_status = "achieved"'],
      },
    ],
  },
  {
    name: 'Collaboration and Interaction',
    color: 'sky',
    desc: 'Quality and nature of the human-AI interaction — agreement, assistance, and time costs.',
    metrics: [
      {
        key: 'human_ai_agreement_rate',
        full: 'Human-AI Agreement Rate',
        unit: '0–1',
        better: 'contextual',
        formula: 'matching_decisions / total',
        desc: 'How often the human and AI reached the same decision or label independently.',
        fields: ['ground_truth / human_label / human_decision', 'prediction / ai_label / ai_decision'],
      },
      {
        key: 'ai_assistance_rate',
        full: 'AI Assistance Rate',
        unit: '0–1',
        better: 'contextual',
        formula: 'assisted_events / total',
        desc: 'Fraction of events where the AI provided active assistance.',
        fields: ['ai_assisted / assisted / ai_help (bool flag)'],
      },
      {
        key: 'decision_effectiveness',
        full: 'Decision Effectiveness',
        unit: '%',
        better: 'higher',
        formula: 'successful_decisions / total × 100',
        desc: 'Percentage of decisions that resulted in a successful outcome.',
        fields: ['decision_outcome = "successful" / "success" / "ok"'],
      },
      {
        key: 'time_to_resolution',
        full: 'Time to Resolution',
        unit: 'seconds',
        better: 'lower',
        formula: 'mean(response_time_s)',
        desc: 'Average elapsed time from problem presentation to resolution.',
        fields: ['response_time / time_to_response / resolution_time  OR  latency_ms'],
      },
      {
        key: 'human_effort_saved',
        full: 'Human Effort Saved',
        unit: 'seconds',
        better: 'higher',
        formula: 'time_without_ai − time_with_ai',
        desc: 'Total time saved across all interactions due to AI assistance.',
        fields: ['time_without_ai', 'time_with_ai'],
      },
    ],
  },
  {
    name: 'Trust and Safety',
    color: 'amber',
    desc: 'Reliability, confidence calibration, and safety record of the AI system.',
    metrics: [
      {
        key: 'confidence',
        full: 'Confidence (Calibration)',
        unit: '%',
        better: 'higher',
        formula: 'high-confidence correct / high-confidence × 100',
        desc: 'Among high-confidence predictions (≥0.9), how many were actually correct — measures calibration.',
        fields: ['confidence_level / confidence (≥0.9 threshold)', 'correct / result = "correct"'],
      },
      {
        key: 'trust_score',
        full: 'Trust Score',
        unit: '%',
        better: 'higher',
        formula: 'trust_rating / trust_scale_maximum × 100',
        desc: 'Subjective trust rating normalised to percentage of the maximum possible score.',
        fields: ['trust_rating', 'trust_scale_maximum'],
      },
      {
        key: 'safety_incidents',
        full: 'Safety Incidents',
        unit: 'count',
        better: 'lower',
        formula: 'sum(safety_incidents)',
        desc: 'Total number of safety-relevant events triggered during the session.',
        fields: ['safety_incidents (numeric count per event)'],
      },
      {
        key: 'system_reliability',
        full: 'System Reliability',
        unit: '%',
        better: 'higher',
        formula: 'uptime / total_time × 100',
        desc: 'Fraction of total session time during which the system was operational.',
        fields: ['uptime', 'total_time'],
      },
    ],
  },
  {
    name: 'Robustness and Generalization',
    color: 'rose',
    desc: 'How well the AI maintains performance under adversarial conditions and across different domains.',
    metrics: [
      {
        key: 'adversarial_robustness',
        full: 'Adversarial Robustness',
        unit: 'ratio',
        better: 'higher (≤1 = degradation)',
        formula: 'performance_adversarial / performance_normal',
        desc: 'Ratio of adversarial to normal performance. 1.0 = no degradation under adversarial inputs.',
        fields: ['performance_adversarial', 'performance_normal'],
      },
      {
        key: 'domain_generalization',
        full: 'Domain Generalization',
        unit: 'ratio',
        better: 'higher',
        formula: 'performance_across_domains / baseline_performance',
        desc: 'How well the AI generalises beyond its training domain, relative to in-domain baseline.',
        fields: ['performance_across_domains', 'baseline_performance'],
      },
    ],
  },
]

// ── Shared UI ─────────────────────────────────────────────────────────────────

const COLORS = {
  indigo:  { border: 'border-indigo-200',  bg: 'bg-indigo-50',  text: 'text-indigo-700',  badge: 'bg-indigo-100 text-indigo-700'   },
  violet:  { border: 'border-violet-200',  bg: 'bg-violet-50',  text: 'text-violet-700',  badge: 'bg-violet-100 text-violet-700'   },
  amber:   { border: 'border-amber-200',   bg: 'bg-amber-50',   text: 'text-amber-700',   badge: 'bg-amber-100 text-amber-700'    },
  emerald: { border: 'border-emerald-200', bg: 'bg-emerald-50', text: 'text-emerald-700', badge: 'bg-emerald-100 text-emerald-700' },
  sky:     { border: 'border-sky-200',     bg: 'bg-sky-50',     text: 'text-sky-700',     badge: 'bg-sky-100 text-sky-700'        },
  rose:    { border: 'border-rose-200',    bg: 'bg-rose-50',    text: 'text-rose-700',    badge: 'bg-rose-100 text-rose-700'      },
}

function PillarSection({ pillar, showFields = false }) {
  const c = COLORS[pillar.color]
  return (
    <section>
      <div className={clsx('rounded-lg border p-4 mb-3', c.border, c.bg)}>
        <h2 className={clsx('text-sm font-semibold', c.text)}>{pillar.name}</h2>
        <p className="text-xs text-gray-600 mt-0.5">{pillar.desc}</p>
      </div>
      <div className="space-y-3">
        {pillar.metrics.map(m => (
          <div key={m.key} className="bg-white rounded-lg border border-gray-200 p-4">
            <div className="flex items-start justify-between gap-4">
              <div className="flex items-center gap-2 min-w-0">
                <span className={clsx('px-2 py-0.5 rounded text-xs font-mono font-bold flex-shrink-0', c.badge)}>
                  {m.key}
                </span>
                <span className="text-sm font-medium text-gray-800 truncate">{m.full}</span>
              </div>
              <div className="text-right flex-shrink-0">
                <p className="text-xs text-gray-400 font-mono">{m.unit}</p>
                <p className="text-xs text-gray-400">better: {m.better}</p>
              </div>
            </div>
            <p className="text-sm text-gray-600 mt-2 leading-relaxed">{m.desc}</p>
            {m.formula && (
              <p className="text-xs font-mono text-gray-500 mt-1.5 bg-gray-50 rounded px-2 py-1 inline-block">
                {m.formula}
              </p>
            )}
            {showFields && m.fields?.length > 0 && (
              <div className="mt-2">
                <p className="text-xs text-gray-400 mb-1">Required log fields:</p>
                <div className="flex flex-wrap gap-1">
                  {m.fields.map((f, i) => (
                    <span key={i} className="text-xs font-mono bg-gray-100 text-gray-600 rounded px-2 py-0.5">
                      {f}
                    </span>
                  ))}
                </div>
              </div>
            )}
            {!showFields && m.range && (
              <p className="text-xs text-gray-400 mt-1.5">
                <span className="font-medium">Range:</span> {m.range}
              </p>
            )}
          </div>
        ))}
      </div>
    </section>
  )
}

// ── Page ──────────────────────────────────────────────────────────────────────

export default function MetricsGlossaryPage() {
  const [tab, setTab] = useState('core')

  return (
    <div className="space-y-6 max-w-3xl">

      <div>
        <h1 className="text-xl font-semibold text-gray-900">Metrics Reference</h1>
        <p className="mt-1 text-sm text-gray-500 leading-relaxed">
          The HAIC benchmark evaluates collaboration across two layers: 8 core interaction metrics
          and up to 29 extended metrics derived from logged event fields.
        </p>
      </div>

      {/* Tab toggle */}
      <div className="flex items-center bg-gray-100 rounded-lg p-1 gap-0.5 w-fit">
        {[['core', 'Core HAIC (8)'], ['extended', 'Extended Metrics (29)']].map(([v, label]) => (
          <button
            key={v}
            onClick={() => setTab(v)}
            className={clsx(
              'px-4 py-1.5 text-sm rounded-md font-medium transition-colors',
              tab === v
                ? 'bg-white shadow-sm text-gray-900'
                : 'text-gray-500 hover:text-gray-700',
            )}
          >
            {label}
          </button>
        ))}
      </div>

      {/* ── Core HAIC tab ── */}
      {tab === 'core' && (
        <div className="space-y-8">
          {CORE_PILLARS.map(p => <PillarSection key={p.name} pillar={p} showFields={false} />)}

          <section>
            <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">
              Domain Benchmark Ranges
            </h2>
            <p className="text-xs text-gray-500 mb-3">
              Reference ranges for Tr, HCL, and EL. Domain is auto-detected from the application
              name and description in your configuration.
            </p>
            <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
              <table className="w-full text-sm">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="text-left px-4 py-2.5 text-xs font-semibold text-gray-500">Domain</th>
                    <th className="text-center px-4 py-2.5 text-xs font-semibold text-gray-500">Tr</th>
                    <th className="text-center px-4 py-2.5 text-xs font-semibold text-gray-500">HCL</th>
                    <th className="text-center px-4 py-2.5 text-xs font-semibold text-gray-500">EL</th>
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
          </section>
        </div>
      )}

      {/* ── Extended Metrics tab ── */}
      {tab === 'extended' && (
        <div className="space-y-8">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-xs text-blue-700 leading-relaxed">
            <strong>How extended metrics work:</strong> Each metric is computed from log event fields
            using flexible aliases. If the required fields are absent from your log, the metric is
            shown as unavailable (gray bar) in the Results dashboard. Add the relevant fields to
            your logs to unlock each metric.
          </div>
          {EXTENDED_PILLARS.map(p => <PillarSection key={p.name} pillar={p} showFields={true} />)}
        </div>
      )}

    </div>
  )
}
