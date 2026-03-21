import { Link } from 'react-router-dom'
import {
  Settings, Compass, FileJson, Upload, BarChart2,
  Download, CheckCircle2, ArrowRight,
} from 'lucide-react'

// ── 5-step guide ───────────────────────────────────────────────────────────

const STEPS = [
  {
    n: 1,
    icon: Settings,
    title: 'Create a Configuration',
    body: 'A configuration is your experiment record. Give it the name of your application, choose the AI model you\'re evaluating, and select which metric groups matter for your use case. You can create as many configurations as you like — one per AI model version is a common pattern.',
    tip: 'Not sure which metric groups to pick? Select all six — you can always focus on specific ones in the results view.',
    href: '/configs',
    action: 'Go to Configurations',
  },
  {
    n: 2,
    icon: Compass,
    title: 'Set Up Your Pilot',
    body: 'Tell the platform how your logs are structured. You\'ll define the action names your system uses, which field records whether the AI was correct, and optionally how long the task takes without AI assistance. This two-minute setup unlocks accurate computation for Trust, Cognitive Load, and Effort Loss.',
    tip: 'Already have logs? Check if they contain actor_type, correct, and duration_s fields. If they do, you may be able to skip this step or use minimal configuration.',
    href: '/pilot/new',
    action: 'Start Pilot Setup',
  },
  {
    n: 3,
    icon: FileJson,
    title: 'Prepare Your Log File',
    body: 'Download a template for your domain below, then fill it with real interaction data from your system. Each log file is a JSON array of sessions. A session groups all the AI and human events that belong to one task attempt. The template includes inline notes explaining every field.',
    tip: 'Start with just 10–20 sessions to validate your setup before uploading a full dataset.',
    href: null,
    action: null,
  },
  {
    n: 4,
    icon: Upload,
    title: 'Upload & Validate',
    body: 'Open the Log Wizard, select your configuration, and upload your JSON file. The platform automatically checks field coverage and tells you which metrics it can compute from your data. If any fields are missing you\'ll see a clear warning — no guessing required.',
    tip: 'The upload step shows a checklist of required fields before you submit. Use it to catch issues early.',
    href: '/ingest',
    action: 'Open Log Wizard',
  },
  {
    n: 5,
    icon: BarChart2,
    title: 'Trigger Evaluation & View Results',
    body: 'Once your logs are uploaded, click Evaluate. Within seconds you\'ll see your HAIC metrics: interaction frequency, trust levels, human cognitive load, effort loss, and more. You can compare multiple AI model versions side by side on the Compare Versions page.',
    tip: 'Re-run evaluation any time — adding more logs and re-evaluating updates your results without losing history.',
    href: '/configs',
    action: 'Browse Results',
  },
]

// ── Template downloads ─────────────────────────────────────────────────────

const TEMPLATES = [
  {
    key: 'applications',
    label: 'Applications',
    emoji: '📋',
    desc: 'Software intake, permit review, or any domain where an AI screens applications and a human operator reviews the decision.',
    file: '/templates/template_applications.json',
    fields: ['ai_evaluated', 'operator_reviewed', 'application_approved / rejected'],
  },
  {
    key: 'healthcare',
    label: 'Healthcare',
    emoji: '🏥',
    desc: 'Medical imaging, clinical decision support, or any domain where an AI produces a diagnosis recommendation and a clinician confirms or overrides it.',
    file: '/templates/template_healthcare.json',
    fields: ['ai_diagnosis', 'radiologist_reviewed', 'diagnosis_confirmed / overridden'],
  },
  {
    key: 'generic',
    label: 'Generic',
    emoji: '⚙️',
    desc: 'Domain-agnostic template with the minimum required fields and inline notes on every key. Best starting point if you\'re unsure how to structure your logs.',
    file: '/templates/template_generic.json',
    fields: ['ai_decision', 'human_review'],
  },
]

// ── Metrics table ──────────────────────────────────────────────────────────

const METRICS_TABLE = [
  {
    metric: 'F, D',
    name: 'Frequency & Duration',
    required: 'timestamps only',
    note: 'always computes',
    always: true,
  },
  {
    metric: 'Tr',
    name: 'Trust',
    required: 'correct: true/false on AI events',
    note: 'add one boolean field per AI event',
    always: false,
  },
  {
    metric: 'HCL',
    name: 'Human Cognitive Load',
    required: 'duration_s or latency_ms',
    note: 'timing fields on events',
    always: false,
  },
  {
    metric: 'EL',
    name: 'Effort Loss',
    required: 'baseline_s in session header',
    note: 'one number per session',
    always: false,
  },
  {
    metric: 'A',
    name: 'Agreement / Alignment',
    required: 'multiple sessions with actor_type on all events',
    note: 'grows with dataset size',
    always: false,
  },
]

// ── Components ─────────────────────────────────────────────────────────────

function StepCard({ step }) {
  const Icon = step.icon
  return (
    <div className="flex gap-5">
      {/* Left: number + connector */}
      <div className="flex flex-col items-center flex-shrink-0">
        <div className="w-10 h-10 rounded-full bg-indigo-600 text-white flex items-center
                        justify-center text-sm font-bold shadow-sm">
          {step.n}
        </div>
        {step.n < STEPS.length && (
          <div className="w-px flex-1 bg-indigo-100 mt-2" style={{ minHeight: 40 }} />
        )}
      </div>

      {/* Right: content */}
      <div className="pb-10 flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-2">
          <Icon size={15} className="text-indigo-500" />
          <h3 className="text-sm font-semibold text-gray-900">{step.title}</h3>
        </div>
        <p className="text-sm text-gray-600 leading-relaxed">{step.body}</p>
        {step.tip && (
          <p className="mt-2 text-xs text-amber-700 bg-amber-50 border border-amber-100
                        rounded-md px-3 py-2 leading-relaxed">
            💡 {step.tip}
          </p>
        )}
        {step.href && (
          <Link
            to={step.href}
            className="inline-flex items-center gap-1.5 mt-3 text-xs font-medium text-indigo-600
                       hover:text-indigo-800 transition-colors"
          >
            {step.action} <ArrowRight size={12} />
          </Link>
        )}
      </div>
    </div>
  )
}

function TemplateCard({ tpl }) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-5 flex flex-col gap-3
                    hover:border-indigo-200 hover:shadow-sm transition-all">
      <div>
        <p className="text-base font-semibold text-gray-900">
          {tpl.emoji} {tpl.label}
        </p>
        <p className="text-xs text-gray-500 mt-1 leading-relaxed">{tpl.desc}</p>
      </div>

      <div>
        <p className="text-xs font-medium text-gray-500 mb-1">Event types in template:</p>
        <div className="flex flex-wrap gap-1">
          {tpl.fields.map((f, i) => (
            <span key={i}
                  className="text-xs font-mono bg-gray-100 text-gray-600 rounded px-1.5 py-0.5">
              {f}
            </span>
          ))}
        </div>
      </div>

      <a
        href={tpl.file}
        download
        className="mt-auto inline-flex items-center gap-2 px-3 py-2 rounded-md text-xs font-medium
                   border border-indigo-200 text-indigo-600 hover:bg-indigo-50 transition-colors
                   self-start"
      >
        <Download size={12} /> Download {tpl.label} template
      </a>
    </div>
  )
}

// ── Page ───────────────────────────────────────────────────────────────────

export default function GettingStartedPage() {
  return (
    <div className="max-w-2xl mx-auto py-6 space-y-12">

      {/* Header */}
      <div>
        <p className="text-xs font-semibold text-indigo-500 uppercase tracking-wider mb-1">
          Getting Started
        </p>
        <h1 className="text-2xl font-bold text-gray-900">
          Run your first evaluation in 5 steps
        </h1>
        <p className="mt-2 text-sm text-gray-500 leading-relaxed">
          No code required. Follow the guide below, download a log template for your domain,
          and you'll have your first HAIC metrics in minutes.
        </p>
      </div>

      {/* 5-step guide */}
      <section>
        <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-6">
          Step-by-step guide
        </h2>
        <div>
          {STEPS.map(step => <StepCard key={step.n} step={step} />)}
        </div>
      </section>

      {/* Download templates */}
      <section>
        <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">
          Log templates
        </h2>
        <p className="text-sm text-gray-500 mb-4">
          Each template is annotated — every field has an inline note explaining what goes there
          and which metric it unlocks. Remove the <code className="font-mono text-xs bg-gray-100 rounded px-1">_note_*</code> keys before uploading.
        </p>
        <div className="grid grid-cols-3 gap-4">
          {TEMPLATES.map(tpl => <TemplateCard key={tpl.key} tpl={tpl} />)}
        </div>
      </section>

      {/* Metrics table */}
      <section>
        <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">
          What metrics will I get?
        </h2>
        <p className="text-sm text-gray-500 mb-4">
          The platform computes whatever your log data supports. Add more fields to unlock more metrics.
        </p>
        <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
          <table className="min-w-full text-sm">
            <thead>
              <tr className="bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                <th className="px-4 py-3 w-20">Metric</th>
                <th className="px-4 py-3 w-36">Name</th>
                <th className="px-4 py-3">Required fields</th>
                <th className="px-4 py-3 w-32">Notes</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {METRICS_TABLE.map(row => (
                <tr key={row.metric} className="hover:bg-gray-50">
                  <td className="px-4 py-3">
                    <span className="font-mono font-semibold text-indigo-700 text-xs">
                      {row.metric}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-xs text-gray-700">{row.name}</td>
                  <td className="px-4 py-3">
                    <code className="text-xs bg-gray-100 text-gray-700 rounded px-1.5 py-0.5 font-mono">
                      {row.required}
                    </code>
                  </td>
                  <td className="px-4 py-3 text-xs text-gray-500">
                    {row.always
                      ? <span className="inline-flex items-center gap-1 text-green-600">
                          <CheckCircle2 size={11} /> always computes
                        </span>
                      : row.note
                    }
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="text-xs text-gray-400 mt-2">
          For the full metrics reference including outcome metrics across 6 pillars, see the{' '}
          <Link to="/metrics" className="text-indigo-500 hover:text-indigo-700 underline underline-offset-2">
            Metrics Reference
          </Link>.
        </p>
      </section>

      {/* CTA */}
      <section className="bg-indigo-50 border border-indigo-100 rounded-xl p-6 flex items-center
                          justify-between gap-4">
        <div>
          <p className="text-sm font-semibold text-gray-900">Ready to start?</p>
          <p className="text-xs text-gray-500 mt-0.5">
            Create your first configuration and upload your logs.
          </p>
        </div>
        <div className="flex gap-3 flex-shrink-0">
          <Link
            to="/pilot/new"
            className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg border border-indigo-200
                       bg-white text-indigo-700 text-sm font-medium hover:border-indigo-400 transition-colors"
          >
            <Compass size={14} /> New Pilot
          </Link>
          <Link
            to="/configs"
            className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-indigo-600
                       text-white text-sm font-medium hover:bg-indigo-700 transition-colors"
          >
            Get Started <ArrowRight size={14} />
          </Link>
        </div>
      </section>

    </div>
  )
}
